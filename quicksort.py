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
    # keep your existing benchmark untouched
    print("Running empirical test...\n")
    run_empirical_test()

    # -----------------------------
    # Static dataset
    # -----------------------------
    sample_data = [42, 15, 73, 8, 65, 29, 91, 34, 50, 11]

    print("\n--- Static Dataset Demonstration ---")
    print("Original Data:", sample_data)

    # Deterministic version
    data_det = sample_data.copy()
    deterministic_quicksort(data_det)
    print("\nDeterministic Quicksort Output:", data_det)

    # Randomized version
    data_rand = sample_data.copy()
    randomized_quicksort(data_rand)
    print("\nRandomized Quicksort Output:", data_rand)