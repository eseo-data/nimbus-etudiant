package nimbus

import Measurement.*

class NimbusTest extends munit.FunSuite:

  test("10.1 Measurement.parse"):
    assertEquals(Measurement.parse("12.5", -40, 50), Valid(12.5))
    assertEquals(Measurement.parse(" NA ", -40, 50), Missing)
    assertEquals(Measurement.parse("vingt", -40, 50), Outlier("vingt", "non numérique"))
    assertEquals(Measurement.parse("999", -40, 50), Outlier("999", "hors bornes"))

  test("10.2 valueOr"):
    assertEquals(Measurement.valueOr(Valid(3.0), 0.0), 3.0)
    assertEquals(Measurement.valueOr(Missing, -1.0), -1.0)

  test("10.3 foldLeft récursif terminal (pas de débordement de pile)"):
    assertEquals(Recursion.foldLeft(List(1, 2, 3), 0)(_ - _), -6)
    assertEquals(Recursion.foldLeft((1 to 1_000_000).toList, 0L)(_ + _), 500000500000L)

  test("10.4 for-compréhension fail-fast"):
    assert(Validation.parseLine("2025-01-01,BREST,10,80").isRight)
    assertEquals(Validation.parseLine("2025/01/01,ATLANTIS,10,80"), Left("date invalide '2025/01/01'"))
    assertEquals(Validation.parseLine("a,b"), Left("attendu 4 colonnes, reçu 2"))

  test("10.5/10.6 monoïde Stats et foldMap"):
    val s = foldMap(List(2.0, 4.0, 9.0))(Stats.of)
    assertEquals(s, Stats(3, 15.0, 2.0, 9.0))
    assertEquals(s.mean, Some(5.0))
    assertEquals(foldMap(List.empty[Double])(Stats.of).mean, None)
    assertEquals(foldMap(List(1.0, 2.0))(identity), 3.0)

  test("10.5 lois du monoïde"):
    val m = summon[Monoid[Stats]]
    val (a, b, c) = (Stats.of(1), Stats.of(-3), Stats.of(7))
    assertEquals(m.empty |+| a, a)
    assertEquals(a |+| m.empty, a)
    assertEquals((a |+| b) |+| c, a |+| (b |+| c))

  test("10.7 catamorphisme sur l'arbre"):
    import Tree.*
    val tree = Node(1, 70.0, Leaf(0.1, 50), Node(2, 1010.0, Leaf(0.8, 30), Leaf(0.4, 20)))
    assertEquals(Tree.depth(tree), 2)
    assertEquals(Tree.fold(tree)((_, n) => n)((_, _, g, d) => g + d), 100)
    assertEquals(Tree.predict(tree, IndexedSeq(0, 90, 1000)), 0.8)
