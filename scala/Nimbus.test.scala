package nimbus

import Mesure.*

class NimbusTest extends munit.FunSuite:

  test("10.1 lire une mesure"):
    assertEquals(Mesure.lire("12.5", -40, 50), Valide(12.5))
    assertEquals(Mesure.lire(" NA ", -40, 50), Manquante)
    assertEquals(Mesure.lire("vingt", -40, 50), Aberrante("vingt", "non numérique"))
    assertEquals(Mesure.lire("999", -40, 50), Aberrante("999", "hors bornes"))

  test("10.2 valeurOu"):
    assertEquals(Mesure.valeurOu(Valide(3.0), 0.0), 3.0)
    assertEquals(Mesure.valeurOu(Manquante, -1.0), -1.0)

  test("10.3 foldLeft récursif terminal (pas de débordement de pile)"):
    assertEquals(Recursion.foldLeft(List(1, 2, 3), 0)(_ - _), -6)
    assertEquals(Recursion.foldLeft((1 to 1_000_000).toList, 0L)(_ + _), 500000500000L)

  test("10.4 for-compréhension fail-fast"):
    assert(Validation.lireLigne("2025-01-01,BREST,10,80").isRight)
    assertEquals(Validation.lireLigne("2025/01/01,ATLANTIS,10,80"), Left("date invalide '2025/01/01'"))
    assertEquals(Validation.lireLigne("a,b"), Left("attendu 4 colonnes, reçu 2"))

  test("10.5/10.6 monoïde Stats et foldMap"):
    val s = foldMap(List(2.0, 4.0, 9.0))(Stats.de)
    assertEquals(s, Stats(3, 15.0, 2.0, 9.0))
    assertEquals(s.moyenne, Some(5.0))
    assertEquals(foldMap(List.empty[Double])(Stats.de).moyenne, None)
    assertEquals(foldMap(List(1.0, 2.0))(identity), 3.0)

  test("10.5 lois du monoïde"):
    val m = summon[Monoide[Stats]]
    val (a, b, c) = (Stats.de(1), Stats.de(-3), Stats.de(7))
    assertEquals(m.vide |+| a, a)
    assertEquals(a |+| m.vide, a)
    assertEquals((a |+| b) |+| c, a |+| (b |+| c))

  test("10.7 catamorphisme sur l'arbre"):
    import Arbre.*
    val arbre = Noeud(1, 70.0, Feuille(0.1, 50), Noeud(2, 1010.0, Feuille(0.8, 30), Feuille(0.4, 20)))
    assertEquals(Arbre.profondeur(arbre), 2)
    assertEquals(Arbre.fold(arbre)((_, n) => n)((_, _, g, d) => g + d), 100)
    assertEquals(Arbre.predire(arbre, IndexedSeq(0, 90, 1000)), 0.8)
