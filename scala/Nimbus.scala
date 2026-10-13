// Séance 10 — Le cœur de Nimbus porté en Scala 3.
// Comparez chaque bloc avec son équivalent Python (séances 3 à 8) :
// ce que Python obtient par discipline, Scala l'impose par le compilateur.

package nimbus

import scala.annotation.tailrec

// ---------------------------------------------------------------------------
// S3 — Types algébriques : un `enum` Scala = le type somme `Mesure` Python.
// Le compilateur VÉRIFIE l'exhaustivité des `match` (essayez d'oublier un cas).
// ---------------------------------------------------------------------------

enum Mesure:
  case Valide(valeur: Double)
  case Manquante
  case Aberrante(brute: String, raison: String)

object Mesure:
  val valeursManquantes: Set[String] = Set("", "NA", "-", "null")

  /** Exercice 10.1 — même spécification que `lire_mesure` (séance 3). Indice : `toDoubleOption`. */
  def lire(brute: String, min: Double, max: Double): Mesure =
    ??? // TODO S10

  /** Exercice 10.2 */
  def valeurOu(m: Mesure, defaut: Double): Double =
    ??? // TODO S10

// ---------------------------------------------------------------------------
// S4 — Récursion terminale : @tailrec fait vérifier par le compilateur que la
// récursion sera transformée en boucle (pas de trampoline nécessaire ici).
// ---------------------------------------------------------------------------

object Recursion:
  /** Exercice 10.3 — fold gauche récursif terminal sur une List Scala (immuable par défaut). */
  // TODO 10.3 : remettre l'annotation @tailrec une fois la récursion écrite
  def foldLeft[A, B](l: List[A], acc: B)(f: (B, A) => B): B =
    ??? // TODO S10

// ---------------------------------------------------------------------------
// S5 — Either + for-compréhension (= flat_map en chaîne, la notation « do » de Haskell)
// ---------------------------------------------------------------------------

final case class Releve(date: String, station: String, temperature: Mesure, humidite: Mesure)

object Validation:
  val stations: Set[String] = Set("VELIZY", "BREST", "LYON")

  def colonnes(ligne: String): Either[String, Array[String]] =
    val c = ligne.split(",", -1)
    if c.length == 4 then Right(c) else Left(s"attendu 4 colonnes, reçu ${c.length}")

  def date(s: String): Either[String, String] =
    scala.util.Try(java.time.LocalDate.parse(s)).toEither.left.map(_ => s"date invalide '$s'").map(_ => s)

  def station(s: String): Either[String, String] =
    if stations.contains(s) then Right(s) else Left(s"station inconnue '$s'")

  /** Exercice 10.4 — enchaîner colonnes, date, station avec une for-compréhension (fail-fast).
    * Ligne simplifiée : date,station,temperature,humidite
    */
  def lireLigne(ligne: String): Either[String, Releve] =
    ??? // TODO S10

// ---------------------------------------------------------------------------
// S6 — Monoïdes comme CLASSES DE TYPES (type classes) : `given` / `using`.
// Python n'a pas d'équivalent direct : on passait le monoïde en argument explicite.
// ---------------------------------------------------------------------------

trait Monoide[A]:
  def vide: A
  extension (a: A) def |+|(b: A): A

final case class Stats(n: Int, somme: Double, mini: Double, maxi: Double):
  def moyenne: Option[Double] = Option.when(n > 0)(somme / n)

object Stats:
  def de(x: Double): Stats = Stats(1, x, x, x)

  /** Exercice 10.5 — l'instance de monoïde pour Stats. */
  given Monoide[Stats] with
    def vide: Stats = ???
    extension (a: Stats) def |+|(b: Stats): Stats = ???

given Monoide[Double] with
  def vide: Double = 0.0
  extension (a: Double) def |+|(b: Double): Double = a + b

/** Exercice 10.6 — foldMap générique : le monoïde est trouvé par le compilateur (`using`). */
def foldMap[A, B](xs: Iterable[A])(f: A => B)(using m: Monoide[B]): B =
  ??? // TODO S10

// ---------------------------------------------------------------------------
// S8 — L'arbre de décision, type somme récursif, et son catamorphisme
// ---------------------------------------------------------------------------

enum Arbre:
  case Feuille(probaPluie: Double, n: Int)
  case Noeud(variable: Int, seuil: Double, gauche: Arbre, droite: Arbre)

object Arbre:
  /** Exercice 10.7 */
  def fold[R](a: Arbre)(fFeuille: (Double, Int) => R)(fNoeud: (Int, Double, R, R) => R): R =
    ??? // TODO S10

  def profondeur(a: Arbre): Int = fold(a)((_, _) => 0)((_, _, g, d) => 1 + g.max(d))

  def predire(a: Arbre, x: IndexedSeq[Double]): Double = a match
    case Feuille(p, _)     => p
    case Noeud(v, s, g, d) => predire(if x(v) <= s then g else d, x)

@main def demo(): Unit =
  val lignes = List("2025-01-01,VELIZY,4.5,88", "2025-01-02,BREST,999,80", "2025/01/03,LYON,3,70")
  lignes.map(Validation.lireLigne).foreach(println)
  val temperatures = lignes.flatMap(l => Validation.lireLigne(l).toOption)
    .map(_.temperature)
    .collect { case Mesure.Valide(v) => v }
  println(foldMap(temperatures)(Stats.de))
