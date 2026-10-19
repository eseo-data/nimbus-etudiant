// Séance 10 — Le cœur de Nimbus porté en Scala 3.
// Comparez chaque bloc avec son équivalent Python (séances 3 à 8) :
// ce que Python obtient par discipline, Scala l'impose par le compilateur.

package nimbus

import scala.annotation.tailrec

// ---------------------------------------------------------------------------
// S3 — Types algébriques : un `enum` Scala = le type somme `Measurement` Python.
// Le compilateur VÉRIFIE l'exhaustivité des `match` (essayez d'oublier un cas).
// ---------------------------------------------------------------------------

enum Measurement:
  case Valid(value: Double)
  case Missing
  case Outlier(raw: String, reason: String)

object Measurement:
  val missingValues: Set[String] = Set("", "NA", "-", "null")

  /** Exercice 10.1 — même spécification que `parse_measurement` (séance 3). Indice : `toDoubleOption`. */
  def parse(raw: String, min: Double, max: Double): Measurement =
    ??? // TODO S10

  /** Exercice 10.2 */
  def valueOr(m: Measurement, default: Double): Double =
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

final case class Reading(date: String, station: String, temperature: Measurement, humidity: Measurement)

object Validation:
  val stations: Set[String] = Set("VELIZY", "BREST", "LYON")

  def columns(line: String): Either[String, Array[String]] =
    val c = line.split(",", -1)
    if c.length == 4 then Right(c) else Left(s"attendu 4 colonnes, reçu ${c.length}")

  def date(s: String): Either[String, String] =
    scala.util.Try(java.time.LocalDate.parse(s)).toEither.left.map(_ => s"date invalide '$s'").map(_ => s)

  def station(s: String): Either[String, String] =
    if stations.contains(s) then Right(s) else Left(s"station inconnue '$s'")

  /** Exercice 10.4 — enchaîner colonnes, date, station avec une for-compréhension (fail-fast).
    * Ligne simplifiée : date,station,temperature,humidite
    */
  def parseLine(line: String): Either[String, Reading] =
    ??? // TODO S10

// ---------------------------------------------------------------------------
// S6 — Monoïdes comme CLASSES DE TYPES (type classes) : `given` / `using`.
// Python n'a pas d'équivalent direct : on passait le monoïde en argument explicite.
// ---------------------------------------------------------------------------

trait Monoid[A]:
  def empty: A
  extension (a: A) def |+|(b: A): A

final case class Stats(n: Int, total: Double, minimum: Double, maximum: Double):
  def mean: Option[Double] = Option.when(n > 0)(total / n)

object Stats:
  def of(x: Double): Stats = Stats(1, x, x, x)

  /** Exercice 10.5 — l'instance de monoïde pour Stats. */
  given Monoid[Stats] with
    def empty: Stats = ???
    extension (a: Stats) def |+|(b: Stats): Stats = ???

given Monoid[Double] with
  def empty: Double = 0.0
  extension (a: Double) def |+|(b: Double): Double = a + b

/** Exercice 10.6 — foldMap générique : le monoïde est trouvé par le compilateur (`using`). */
def foldMap[A, B](xs: Iterable[A])(f: A => B)(using m: Monoid[B]): B =
  ??? // TODO S10

// ---------------------------------------------------------------------------
// S8 — L'arbre de décision, type somme récursif, et son catamorphisme
// ---------------------------------------------------------------------------

enum Tree:
  case Leaf(rainProbability: Double, n: Int)
  case Node(variable: Int, threshold: Double, left: Tree, right: Tree)

object Tree:
  /** Exercice 10.7 */
  def fold[R](a: Tree)(fLeaf: (Double, Int) => R)(fNode: (Int, Double, R, R) => R): R =
    ??? // TODO S10

  def depth(a: Tree): Int = fold(a)((_, _) => 0)((_, _, g, d) => 1 + g.max(d))

  def predict(a: Tree, x: IndexedSeq[Double]): Double = a match
    case Leaf(p, _)     => p
    case Node(v, s, g, d) => predict(if x(v) <= s then g else d, x)

@main def demo(): Unit =
  val lines = List("2025-01-01,VELIZY,4.5,88", "2025-01-02,BREST,999,80", "2025/01/03,LYON,3,70")
  lines.map(Validation.parseLine).foreach(println)
  val temperatures = lines.flatMap(l => Validation.parseLine(l).toOption)
    .map(_.temperature)
    .collect { case Measurement.Valid(v) => v }
  println(foldMap(temperatures)(Stats.of))
