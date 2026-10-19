"""Bloc BD3 — stream processing en pur."""

from types import MappingProxyType

import pytest
from hypothesis import given, settings
from hypothesis import strategies as st

from nimbus.bd3_streaming import (
    State, Event, aggregate_batch, window_start, disorder, step, events_from_csv,
    process, flush,
)
from nimbus.datagen import generate_massive_lines

SIZE, DELAY = 7, 3


def evts(*triplets):
    return [Event(f"{s}-{t}-{v}", s, t, v) for s, t, v in triplets]


def streaming_result(events, size=SIZE, delay=DELAY):
    state, outputs = process(events, size, delay)
    state, rest = flush(state, size)
    return state, {(f.station, f.start): f.stats for f in outputs + rest}


def test_window_start():
    assert [window_start(t, 7) for t in (0, 6, 7, 13, 14)] == [0, 0, 7, 7, 14]


def test_step_does_not_mutate_state():
    e0 = State()
    e1, outputs = step(e0, Event("a", "S", 3, 10.0), SIZE, DELAY)
    assert e0 == State() and outputs == ()
    assert isinstance(e1.open_windows, MappingProxyType)
    assert e1.open_windows[("S", 0)].n == 1 and e1.watermark == 0


def test_window_emitted_when_watermark_passes():
    state, outputs = process(evts(("S", 1, 10.0), ("S", 2, 12.0), ("S", 9, 5.0)), SIZE, DELAY)
    assert outputs == () and state.watermark == 6              # [0, 7) encore ouverte
    state, outputs = process(evts(("S", 10, 6.0)), SIZE, DELAY, state)
    assert state.watermark == 7                                # 10 - 3 : [0, 7) se ferme
    assert [(f.start, f.stats.n, f.stats.average) for f in outputs] == [(0, 2, 11.0)]


def test_delay_and_duplicate():
    stream = evts(("S", 1, 10.0), ("S", 20, 5.0))            # watermark = 17 : [0, 7) est fermée
    stream += [Event("tardif", "S", 2, 99.0), stream[0]]   # un événement en retard, un doublon
    state, outputs = process(stream, SIZE, DELAY)
    assert state.delays == 1 and state.duplicates == 1
    assert outputs[0].stats.n == 1                            # le tardif n'a pas été compté


@pytest.fixture(scope="module")
def real_stream():
    # un vrai flux arrive dans l'ordre du temps, toutes stations mélangées
    return sorted(events_from_csv(generate_massive_lines(5, 6, 365)), key=lambda e: (e.timestamp, e.station))


def test_ordered_streaming_equals_batch(real_stream):
    state, streaming = streaming_result(real_stream)
    batch = aggregate_batch(real_stream, SIZE)
    assert state.delays == 0 and streaming.keys() == batch.keys()
    assert all(streaming[k].n == batch[k].n and abs(streaming[k].total - batch[k].total) < 1e-6 for k in batch)


def test_bounded_disorder_same_result(real_stream):
    # le désordre reste inférieur au retard toléré : même résultat qu'en ordre
    shuffled = disorder(real_stream, 6 * 3, 2026)          # paquets d'environ 3 jours × 6 stations
    _, ordered_stats = streaming_result(real_stream)
    state, disordered_stats = streaming_result(shuffled)
    assert state.delays == 0
    assert {k: v.n for k, v in disordered_stats.items()} == {k: v.n for k, v in ordered_stats.items()}


def test_checkpoint_and_replay(real_stream):
    middle = len(real_stream) // 2
    state1, s1 = process(real_stream[:middle], SIZE, DELAY)
    state2, s2 = process(real_stream[middle:], SIZE, DELAY, state1)       # reprise après checkpoint
    full_state, s_all = process(real_stream, SIZE, DELAY)
    assert s1 + s2 == s_all and state2 == full_state
    assert process(real_stream, SIZE, DELAY) == (full_state, s_all)    # replay


@settings(max_examples=60, deadline=None)
@given(st.lists(st.tuples(st.sampled_from("AB"), st.integers(0, 60), st.integers(-20, 30)), max_size=80))
def test_replaying_duplicates_changes_nothing(triplets):
    stream = evts(*triplets)
    assert streaming_result(stream)[1].keys() == streaming_result(stream + stream)[1].keys()
    assert {k: v.n for k, v in streaming_result(stream + stream)[1].items()} == \
           {k: v.n for k, v in streaming_result(stream)[1].items()}
