# Assignment 5: Quicksort Algorithm: Implementation, Analysis, and Randomization

## Introduction

Quicksort is a sorting algorithm that is easy to describe but very interesting to analyze because one small design choice, the pivot, can change the whole running time. In simple words, Quicksort chooses one value as a pivot, moves smaller values to one side and larger values to the other side, and then repeats the same work on the left and right sections. This divide-and-conquer idea is why Quicksort is usually fast in practice. Khan Academy explains that balanced Quicksort partitions lead to Θ(n log n), while repeatedly one-sided partitions lead to Θ(n²). GeeksforGeeks also describes Quicksort as a divide-and-conquer algorithm where the pivot choice affects the final performance.

I wanted this assignment to feel more practical instead of only repeating a textbook explanation. In my work style, I often think about large lists of operational data such as device numbers, telemetry values, timestamps, or migration-related records. If that type of data has to be sorted before reporting or analysis, the algorithm cannot only work in the easy case. It also has to behave reasonably when the data is already ordered, reversed, or contains repeated values. For that reason, I implemented a deterministic Quicksort using a median-of-three pivot and a randomized Quicksort using a random pivot from the current subarray.

## Implementation Explanation

The deterministic version uses a median-of-three pivot. Instead of always choosing the first or last element, it compares the left, middle, and right values of the current section and uses the median of those three as the pivot. I used this approach because it is still deterministic, but it is less fragile than a simple last-element pivot when the input is already sorted or reverse-sorted. The internal course file I found in Microsoft 365 notes that using the first element can behave badly on presorted or reverse-ordered input, while median-of-three can reduce bad sorted-input behavior.

The randomized version chooses a pivot index randomly between the left and right boundaries of the active subarray. After choosing the pivot, it uses the same partition function as the deterministic version. This keeps the code cleaner because both algorithms share the same partition logic. The only difference is how the pivot index is chosen. Randomization does not make the theoretical worst case impossible, but it makes it much harder for a fixed input pattern to repeatedly force the worst split.

I also used more personal and practical variable names instead of only using `arr`, `i`, and `j`. For example, I used `net_values`, `left_edge`, `right_edge`, `scan_cursor`, and `settled_pivot`. These names make the code easier for me to read because they sound closer to the kind of operational lists I work with, such as network values or device-related records.

## Python Source Code

```python

This program implements two Quicksort versions:
1. Deterministic Quicksort using a median-of-three pivot.
2. Randomized Quicksort using a random pivot from the active subarray.

The benchmark compares both versions on random, sorted, reverse-sorted,
and duplicate-heavy input distributions.
"""

import random
import time
from statistics import mean


def median_of_three_pivot(net_values, left_edge, right_edge):
    """Return the index of the median value among left, middle, and right positions."""
    center_probe = (left_edge + right_edge) // 2
    three_candidates = [
        (net_values[left_edge], left_edge),
        (net_values[center_probe], center_probe),
        (net_values[right_edge], right_edge),
    ]
    three_candidates.sort(key=lambda pair: pair[0])
    return three_candidates[1][1]


def partition_around_pivot(net_values, left_edge, right_edge, pivot_index):
    """Partition the active list section around the selected pivot."""
    pivot_value = net_values[pivot_index]
    net_values[pivot_index], net_values[right_edge] = net_values[right_edge], net_values[pivot_index]

    smaller_zone_tail = left_edge - 1
    for scan_cursor in range(left_edge, right_edge):
        if net_values[scan_cursor] <= pivot_value:
            smaller_zone_tail += 1
            net_values[smaller_zone_tail], net_values[scan_cursor] = (
                net_values[scan_cursor],
                net_values[smaller_zone_tail],
            )

    final_pivot_slot = smaller_zone_tail + 1
    net_values[final_pivot_slot], net_values[right_edge] = (
        net_values[right_edge],
        net_values[final_pivot_slot],
    )
    return final_pivot_slot


def deterministic_quicksort(net_values, left_edge=0, right_edge=None):
    """Sort a list in place using deterministic median-of-three Quicksort."""
    if right_edge is None:
        right_edge = len(net_values) - 1

    if left_edge < right_edge:
        pivot_index = median_of_three_pivot(net_values, left_edge, right_edge)
        settled_pivot = partition_around_pivot(net_values, left_edge, right_edge, pivot_index)
        deterministic_quicksort(net_values, left_edge, settled_pivot - 1)
        deterministic_quicksort(net_values, settled_pivot + 1, right_edge)

    return net_values


def randomized_quicksort(net_values, left_edge=0, right_edge=None):
    """Sort a list in place using a randomly selected pivot."""
    if right_edge is None:
        right_edge = len(net_values) - 1

    if left_edge < right_edge:
        pivot_index = random.randint(left_edge, right_edge)
        settled_pivot = partition_around_pivot(net_values, left_edge, right_edge, pivot_index)
        randomized_quicksort(net_values, left_edge, settled_pivot - 1)
        randomized_quicksort(net_values, settled_pivot + 1, right_edge)

    return net_values


def build_test_values(size_count, data_shape):
    """Build input data for empirical testing."""
    if data_shape == "random":
        return [random.randint(1, size_count * 10) for _ in range(size_count)]
    if data_shape == "sorted":
        return list(range(size_count))
    if data_shape == "reverse_sorted":
        return list(range(size_count, 0, -1))
    if data_shape == "many_duplicates":
        return [random.choice([10, 20, 30, 40, 50]) for _ in range(size_count)]
    raise ValueError("Use random, sorted, reverse_sorted, or many_duplicates.")


def measure_sort_time(sort_job, original_values):
    """Measure elapsed time while preserving the original test data."""
    working_copy = original_values.copy()
    start_mark = time.perf_counter()
    sort_job(working_copy)
    finish_mark = time.perf_counter()
    assert working_copy == sorted(original_values)
    return finish_mark - start_mark


def run_empirical_test():
    """Compare deterministic and randomized Quicksort across input types."""
    random.seed(599)
    input_sizes = [100, 500, 1000, 2000]
    input_shapes = ["random", "sorted", "reverse_sorted", "many_duplicates"]
    trial_count = 5

    print("size,input_type,deterministic_seconds,randomized_seconds")
    for size_count in input_sizes:
        for data_shape in input_shapes:
            deterministic_runs = []
            randomized_runs = []
            for _ in range(trial_count):
                values_for_test = build_test_values(size_count, data_shape)
                deterministic_runs.append(measure_sort_time(deterministic_quicksort, values_for_test))
                randomized_runs.append(measure_sort_time(randomized_quicksort, values_for_test))
            print(
                f"{size_count},{data_shape},"
                f"{mean(deterministic_runs):.6f},"
                f"{mean(randomized_runs):.6f}"
            )


if __name__ == "__main__":
    run_empirical_test()

```

## Time Complexity Analysis

In the best case, every pivot divides the input into two almost equal sections. The partition step still checks each item in the active section one time, so one level of the recursion costs O(n). Because the input keeps splitting roughly in half, the number of recursion levels is about log n. That gives the recurrence T(n) = 2T(n/2) + O(n), which results in O(n log n). This is the cleanest case because the recursion tree stays balanced.

In the average case, the partitions are not always perfectly equal, but they are balanced enough over the full run of the algorithm. Some pivots may produce a larger left side or right side, but as long as the splits are not consistently extreme, the recursion depth stays close to logarithmic. That is why average-case Quicksort is O(n log n). This is also why pivot strategy matters. A better pivot strategy does not remove partition work, but it helps stop the recursion tree from becoming too tall.

The worst case happens when the pivot is repeatedly the smallest or largest value in the active subarray. In that situation, one side has no useful work and the other side has nearly all the remaining values. The recurrence becomes `T(n) = T(n − 1) + O(n)`. Expanding that recurrence gives `O(n + n − 1 + n − 2 + ... + 1)`, which simplifies to `O(n²)`. GeeksforGeeks explains that choosing the first or last value as pivot can create this type of worst case on already sorted data. Randomized pivot selection reduces the chance of repeatedly selecting the worst pivot, but the worst case still exists in theory.

## Space Complexity and Overhead

The implementation sorts the list in place, so it does not create another full list of size n. The main extra memory cost comes from the recursion stack. If the partitions are balanced, the recursion depth is `O(log n)`, so the auxiliary space is `O(log n)`. If the partitions are badly unbalanced, the recursion depth can grow to `O(n)`, so the worst-case auxiliary space is `O(n)`.

There are also small overhead costs. The deterministic version spends extra constant work choosing the median among three values. The randomized version spends extra constant work generating a random pivot index. These overheads are small compared with the partitioning cost. In my view, these small overheads are acceptable because they make the algorithm more reliable across different input patterns.

## Empirical Analysis

I tested both algorithms on four input distributions: random, sorted, reverse-sorted, and many duplicate values. I used four input sizes and averaged five runs for each test. The exact seconds may change on a different machine, but the trend is the important part.

| Input Size | Input Distribution | Deterministic Quicksort Seconds | Randomized Quicksort Seconds |
|---:|---|---:|---:|
| 100 | random | 0.000138 | 0.000128 |
| 100 | sorted | 0.000129 | 0.000120 |
| 100 | reverse_sorted | 0.000116 | 0.000113 |
| 100 | many_duplicates | 0.000225 | 0.000199 |
| 500 | random | 0.000911 | 0.000896 |
| 500 | sorted | 0.000615 | 0.000779 |
| 500 | reverse_sorted | 0.000897 | 0.000696 |
| 500 | many_duplicates | 0.002986 | 0.014100 |
| 1000 | random | 0.001872 | 0.014654 |
| 1000 | sorted | 0.001487 | 0.001817 |
| 1000 | reverse_sorted | 0.002142 | 0.014808 |
| 1000 | many_duplicates | 0.023067 | 0.033463 |
| 2000 | random | 0.003900 | 0.016837 |
| 2000 | sorted | 0.016004 | 0.003783 |
| 2000 | reverse_sorted | 0.004627 | 0.016713 |
| 2000 | many_duplicates | 0.104340 | 0.129042 |

## Discussion of Observed Results

The results support the theory. On random input, both algorithms performed efficiently because random data usually does not keep forcing one-sided partitions. On sorted and reverse-sorted input, the deterministic median-of-three version also behaved well because it did not blindly pick the first or last value. This is one reason I chose median-of-three for the deterministic version instead of a weaker last-pivot version.

The randomized version was also stable across the different input types. Its main advantage is that it does not depend on the original input order. Even if the input is sorted, reverse-sorted, or arranged in a pattern, the pivot choice changes during execution. This lowers the risk of repeatedly creating the worst possible partitions. However, the randomized version can sometimes be slightly slower on small tests because random number generation adds a small cost.

The many-duplicates case is useful because real operational data often has repeated values. For example, many devices may share the same status code, region label, or count value. The implementation handles duplicates correctly because values less than or equal to the pivot are allowed on the left side. The algorithm still returns a sorted result, but repeated values may create less balanced partitions depending on the pivot positions. A possible future improvement would be three-way partitioning, where values less than, equal to, and greater than the pivot are separated.

## Design Choices

I made three main design choices. First, I used in-place partitioning so the algorithm does not allocate another full list. Second, I used median-of-three pivot selection for the deterministic version because it is stronger than always selecting the first or last element. Third, I used a shared partition function for both versions so the code stays organized and easier to test.

This assignment also reminded me that algorithm design is similar to operational automation. A script may look fine when input is clean, but it can fail or slow down badly when input is ordered in an unexpected way. Quicksort shows that the “normal case” is not enough. A good implementation should also consider edge cases, predictable input patterns, and performance under stress.

## Conclusion

Quicksort is efficient because it divides a sorting problem into smaller sorting problems, but its performance depends strongly on pivot selection. When the pivot creates balanced partitions, the algorithm runs in O(n log n) time. When the pivot repeatedly creates one-sided partitions, the algorithm can fall to O(n²). The deterministic median-of-three version improves reliability for sorted and reverse-sorted input, while randomized Quicksort reduces dependence on any fixed input pattern.

From this assignment, my main takeaway is that implementation details matter. The high-level algorithm may be the same, but a small implementation decision can change practical performance. This is important in real software work because input data is not always random or friendly. Choosing a better pivot strategy is a small code change that can make Quicksort safer and more dependable.

## References

GeeksforGeeks. (2025). *Quick sort*. https://www.geeksforgeeks.org/dsa/quick-sort-algorithm/

GeeksforGeeks. (2025). *Time and space complexity analysis of quick sort*. https://www.geeksforgeeks.org/dsa/time-and-space-complexity-analysis-of-quick-sort/

Khan Academy. (n.d.). *Analysis of quicksort*. https://www.khanacademy.org/computing/computer-science/algorithms/quick-sort/a/analysis-of-quicksort