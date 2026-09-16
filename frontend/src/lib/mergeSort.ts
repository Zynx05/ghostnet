/**
 * Member 3  Frontend Developer
 * Merge sort in TypeScript.
 *
 * The backend already returns ranked rows. This runs again in the browser when
 * the user clicks a column header, so the table can be reordered without asking
 * the server for anything.
 *
 * Complexity: O(n log n) in the best, average and worst case.
 * Stability matters here: two submissions on the same score must keep the order
 * they arrived in, otherwise the table jumps around on every click.
 */

export type Direction = 'asc' | 'desc';

export function mergeSort<T>(
  items: T[],
  key: (item: T) => number | string,
  direction: Direction = 'desc',
): T[] {
  if (items.length <= 1) return [...items];
  const middle = Math.floor(items.length / 2);
  const left = mergeSort(items.slice(0, middle), key, direction);
  const right = mergeSort(items.slice(middle), key, direction);
  return merge(left, right, key, direction);
}

function merge<T>(
  left: T[],
  right: T[],
  key: (item: T) => number | string,
  direction: Direction,
): T[] {
  const out: T[] = [];
  let i = 0;
  let j = 0;

  while (i < left.length && j < right.length) {
    const a = key(left[i]);
    const b = key(right[j]);
    // A tie takes the left item, and that is what keeps the sort stable.
    const leftFirst = direction === 'desc' ? a >= b : a <= b;
    if (leftFirst) {
      out.push(left[i]);
      i += 1;
    } else {
      out.push(right[j]);
      j += 1;
    }
  }

  return out.concat(left.slice(i)).concat(right.slice(j));
}
