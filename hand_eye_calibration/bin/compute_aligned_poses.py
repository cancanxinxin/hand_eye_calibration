#!/usr/bin/env python
from hand_eye_calibration.time_alignment import (
    calculate_time_offset, compute_aligned_poses, FilteringConfig)
from hand_eye_calibration.quaternion import Quaternion
import argparse
import numpy as np
import csv


def read_time_stamped_poses_from_csv_file(csv_file):
  """
  Reads time stamped poses from a CSV file.
  Assumes the following line format:
    timestamp [s], x [m], y [m], z [m], qx, qy, qz, qw
  """
  with open(csv_file, 'r') as csvfile:
    csv_reader = csv.reader(csvfile, delimiter=',', quotechar='|')
    time_stamped_poses = np.array(list(csv_reader))
    time_stamped_poses = time_stamped_poses.astype(float)

  # Extract the quaternions from the poses.
  times = time_stamped_poses[:, 0].copy()
  poses = time_stamped_poses[:, 1:]

  quaternions = []
  for pose in poses:
    quaternions.append(Quaternion(q=pose[3:]))

  return (time_stamped_poses.copy(), times, quaternions)


def write_time_stamped_poses_to_csv_file(time_stamped_poses, csv_file):
  """
  Writes time stamped poses to a CSV file.
  Uses the following line format:
    timestamp [s], x [m], y [m], z [m], qx, qy, qz, qw
  """
  np.savetxt(csv_file, time_stamped_poses, delimiter=", ", fmt="%.18f")


if __name__ == '__main__':
  """
  Perform time alignment between two timestamped sets of poses and
  compute time-aligned poses pairs.

  The CSV files should have the following line format:
    timestamp [s], x [m], y [m], z [m], qx, qy, qz, qw

  The resulting aligned poses follow the same format.
  """

  parser = argparse.ArgumentParser(description=__doc__)
  parser.add_argument(
      '--poses_B_H_csv_file',
      required=True,
      help='The CSV file containing the first time stamped poses. (e.g. Hand poses in Body frame)')
  parser.add_argument(
      '--poses_W_E_csv_file',
      required=True,
      help='The CSV file containing the second time stamped poses. (e.g. Eye poses in World frame)')

  parser.add_argument(
      '--aligned_poses_B_H_csv_file',
      required=True,
      help='Path to the CSV file where the aligned poses will be stored. (e.g. Hand poses in Body frame)')
  parser.add_argument(
      '--aligned_poses_W_E_csv_file',
      required=True,
      help='Path to the CSV file where the aligned poses will be stored. (e.g. Eye poses in World frame)')

  args = parser.parse_args()

  print("Reading CSV files...")
  (time_stamped_poses_B_H, times_B_H, quaternions_B_H
   ) = read_time_stamped_poses_from_csv_file(args.poses_B_H_csv_file)
  print("Found ", time_stamped_poses_B_H.shape[
      0], " poses in file: ", args.poses_B_H_csv_file)

  (time_stamped_poses_W_E, times_W_E, quaternions_W_E
   ) = read_time_stamped_poses_from_csv_file(args.poses_W_E_csv_file)
  print("Found ", time_stamped_poses_W_E.shape[
      0], " poses in file: ", args.poses_W_E_csv_file)

  print("Computing time offset...")
  filtering_config = FilteringConfig()
  # TODO(mfehr): get filtering config from args!
  time_offset = calculate_time_offset(times_B_H, quaternions_B_H, times_W_E,
                                      quaternions_W_E, filtering_config)

  print("Final time offset: ", time_offset, "s")

  print("Computing aligned poses...")
  (aligned_poses_B_H, aligned_poses_W_E) = compute_aligned_poses(
      time_stamped_poses_B_H, time_stamped_poses_W_E, time_offset, True)

  print("Writing aligned poses to CSV files...")
  write_time_stamped_poses_to_csv_file(aligned_poses_B_H,
                                       args.aligned_poses_B_H_csv_file)
  write_time_stamped_poses_to_csv_file(aligned_poses_W_E,
                                       args.aligned_poses_W_E_csv_file)
