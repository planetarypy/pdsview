#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdsview import pdsview
import os

FILE_1 = os.path.join(
    'tests', 'mission_data', '2m132591087cfd1800p2977m2f1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_4 = os.path.join(
    'tests', 'mission_data', 'r01090al.img')
FILE_5 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')
FILE_6 = os.path.join(
    'tests', 'mission_data', '0047MH0000110010100214C00_DRCL.IMG')
FILE_1_NAME = '2m132591087cfd1800p2977m2f1.img'
FILE_2_NAME = '2p129641989eth0361p2600r8m1.img'
FILE_3_NAME = '1p190678905erp64kcp2600l8c1.img'
FILE_4_NAME = 'r01090al.img'
FILE_5_NAME = '1p134482118erp0902p2600r8m1.img'
FILE_6_NAME = '0047MH0000110010100214C00_DRCL.IMG'


def test_image_stamp_1():
    """Test that ImageStamp sets correct attributes to pds compatible image"""
    test_image = pdsview.ImageStamp(FILE_1)
    assert test_image.file_name == FILE_1_NAME
    assert 'PDS' in test_image.label[0]
    assert isinstance(test_image.label, list)
    assert test_image.pds_compatible


def test_image_stamp_2():
    """Test that ImageStamp sets correct attributes to pds compatible image"""
    test_image = pdsview.ImageStamp(FILE_6)
    assert test_image.file_name == FILE_6_NAME
    assert not(test_image.pds_compatible)


def test_image_set_1():
    """Test ImageSet with one pds compatible image"""
    filepaths = [FILE_4]
    test_set = pdsview.ImageSet(filepaths)
    assert len(test_set.images) > 0
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_4_NAME
    assert test_set.current_image.pds_compatible
    assert not(test_set.next_prev_enabled)


def test_image_set_2():
    """Test duplicates removed & pds incompatible files not added to images"""
    filepaths = [FILE_4, FILE_4, FILE_5, FILE_6]
    test_set = pdsview.ImageSet(filepaths)
    # Test duplicates are deleted
    assert len(test_set.inlist) < len(filepaths)
    # Test order is preserved
    for n in range(len(test_set.inlist)):
        assert filepaths[n+1] == test_set.inlist[n]
    # Test non-pds compatible images (FILE_7) are not added to images list
    assert len(test_set.inlist) > len(test_set.images)
    # Test that next/previous will be enabled
    assert test_set.next_prev_enabled


def test_image_set_next_method():
    """Test the next method & that loops to beginning if at the last image"""
    filepaths = [FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_3_NAME
    test_set.next()
    assert test_set.current_image_index == 1
    assert test_set.current_image.file_name == FILE_4_NAME
    test_set.next()
    assert test_set.current_image_index == 2
    assert test_set.current_image.file_name == FILE_5_NAME
    test_set.next()
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_3_NAME


def test_image_set_previous_method():
    """Test the previous method & loops to end if at the first image"""
    filepaths = [FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_3_NAME
    test_set.previous()
    assert test_set.current_image_index == 2
    assert test_set.current_image.file_name == FILE_5_NAME
    test_set.previous()
    assert test_set.current_image_index == 1
    assert test_set.current_image.file_name == FILE_4_NAME
    test_set.previous()
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_3_NAME


def test_image_set_append_method_1():
    """Test append method with adding one image"""
    filepaths = [FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_3_NAME
    # Mimic how append method is used in pdsview
    assert len(test_set.images) == 3
    new_image = test_set.append(FILE_2, len(test_set.images))
    assert len(test_set.images) == 4
    assert new_image == test_set.current_image
    assert test_set.current_image_index == 3
    assert new_image.file_name == FILE_2_NAME
    assert test_set.current_image.file_name == FILE_2_NAME


def test_image_set_append_method_2():
    """Test append method with multiple images"""
    filepaths = [FILE_1]
    new_files = [FILE_2, FILE_3]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image.file_name == FILE_1_NAME
    assert len(test_set.images) == 1
    assert not(test_set.next_prev_enabled)
    # Mimic how append method is used in pdsview
    first_new_image = len(test_set.images)
    for new_file in new_files:
        test_set.append(new_file, first_new_image)
    assert test_set.current_image_index == 1
    assert test_set.current_image.file_name == FILE_2_NAME
    assert FILE_3_NAME in str(test_set.images)
    assert test_set.next_prev_enabled


def test_ROI_data():
    """Test the ROI_data to cut out the correct region of data"""
    test_set = pdsview.ImageSet([FILE_3])
    test_data_1 = test_set.ROI_data(
        0, 0, test_set.current_image.width, test_set.current_image.height)
    assert test_data_1[0][0] == 23
    assert test_data_1[512][16] == 25
    assert test_data_1[1023][31] == 115
    test_data_2 = test_set.ROI_data(9.5, 18.5, 11.5, 20.5)
    assert test_data_2[0][0] == 22
    assert test_data_2[0][1] == 23
    assert test_data_2[1][0] == 24
    assert test_data_2[1][1] == 24


def test_ROI_pixels():
    """Test ROI_pixels to return the correct number of pixels for a ROI"""
    test_set = pdsview.ImageSet([FILE_3])
    test_pixels = test_set.ROI_pixels(9.5, 18.5, 11.5, 20.5)
    assert test_pixels == 4


def test_ROI_std_dev():
    """Test ROI_std_dev to return the correct standard deviation for a ROI"""
    test_set = pdsview.ImageSet([FILE_3])
    test_std_dev = test_set.ROI_std_dev(9.5, 18.5, 11.5, 20.5)
    assert test_std_dev == 0.829156


def test_ROI_mean():
    """Test ROI_mean to return the correct mean value of pixels for a ROI"""
    test_set = pdsview.ImageSet([FILE_3])
    test_mean = test_set.ROI_mean(9.5, 18.5, 11.5, 20.5)
    assert test_mean == 23.25


def test_ROI_median():
    """Test ROI_median to return the correct median value for a ROI"""
    test_set = pdsview.ImageSet([FILE_3])
    test_median = test_set.ROI_median(9.5, 18.5, 11.5, 20.5)
    assert test_median == 23.5


def test_ROI_min():
    """Test ROI_min to return the correct minimum pixel value for a ROI"""
    test_set = pdsview.ImageSet([FILE_3])
    test_min = test_set.ROI_min(9.5, 18.5, 11.5, 20.5)
    assert test_min == 22


def test_ROI_max():
    """Test ROI_mx to return the correct maximum pixel value for a ROI"""
    test_set = pdsview.ImageSet([FILE_3])
    test_max = test_set.ROI_max(9.5, 18.5, 11.5, 20.5)
    assert test_max == 24
