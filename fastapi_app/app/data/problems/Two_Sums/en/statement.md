# Two Sum

## Problem Statement
Given an array of integers `nums` and an integer `target`. Find two numbers such that their sum equals `target`.

Return the indices of these numbers in the array (0-indexed). You may assume that each input has exactly one solution. You may not use the same element twice.

## Input Format
The first line contains an integer $n$ — the number of elements in the array ($1 \le n \le 10^5$).

The second line contains $n$ integers $a_1, a_2, \ldots, a_n$ ($-10^9 \le a_i \le 10^9$).

The third line contains an integer $target$ ($-2 \cdot 10^9 \le target \le 2 \cdot 10^9$).

## Output Format
Output two numbers — the indices of the array elements whose sum equals `target`.

## Examples

| Input | Output |
|-------|--------|
| 4<br>2 7 11 15<br>9 | 0 1 |
| 3<br>3 2 4<br>6 | 1 2 |
| 2<br>3 3<br>6 | 0 1 |
