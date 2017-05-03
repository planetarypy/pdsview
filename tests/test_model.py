#!/usr/bin/env python
# -*- coding: utf-8 -*-
from pdsview import pdsview
import os
from planetaryimage import PDS3Image

FILE_1 = os.path.join(
    'tests', 'mission_data', '2m132591087cfd1800p2977m2f1.img')
FILE_2 = os.path.join(
    'tests', 'mission_data', '2p129641989eth0361p2600r8m1.img')
FILE_3 = os.path.join(
    'tests', 'mission_data', '1p190678905erp64kcp2600l8c1.img')
FILE_4 = os.path.join(
    'tests', 'mission_data', 'h58n3118.img')
FILE_5 = os.path.join(
    'tests', 'mission_data', '1p134482118erp0902p2600r8m1.img')
FILE_6 = os.path.join(
    'tests', 'mission_data', '0047MH0000110010100214C00_DRCL.IMG')
FILE_1_NAME = '2m132591087cfd1800p2977m2f1.img'
FILE_2_NAME = '2p129641989eth0361p2600r8m1.img'
FILE_3_NAME = '1p190678905erp64kcp2600l8c1.img'
FILE_4_NAME = 'h58n3118.img'
FILE_5_NAME = '1p134482118erp0902p2600r8m1.img'
FILE_6_NAME = '0047MH0000110010100214C00_DRCL.IMG'


def test_image_stamp():
    """Test that ImageStamp sets correct attributes to pds compatible image"""
    pds_image = PDS3Image.open(FILE_1)
    test_image = pdsview.ImageStamp(FILE_1, FILE_1, pds_image, pds_image.data)
    assert test_image.file_name == FILE_1_NAME
    assert test_image.image_name == FILE_1
    assert 'PDS' in test_image.label[0]
    assert isinstance(test_image.label, list)
    assert not test_image.cuts
    assert not test_image.sarr
    assert not test_image.zoom
    assert not test_image.rotation
    assert not test_image.transforms
    assert test_image.not_been_displayed


def test_image_set_1():
    """Test ImageSet with one pds compatible image"""
    filepaths = [FILE_4]
    test_set = pdsview.ImageSet(filepaths)
    assert len(test_set.images) == 1
    assert len(test_set.file_dict) == 1
    assert test_set.current_image_index == 0
    assert isinstance(test_set.current_image, list)
    assert test_set.current_image[0].file_name == FILE_4_NAME
    assert not(test_set.next_prev_enabled)


def test_image_set_2():
    """Test duplicates removed & pds incompatible files not added to images"""
    filepaths = [FILE_4, FILE_4, FILE_5, FILE_6]
    test_set = pdsview.ImageSet(filepaths)
    # Test duplicates are deleted
    assert len(test_set.images) < len(filepaths)
    # Test the list is sorted
    assert test_set.images[0][0].image_name == FILE_5_NAME
    assert test_set.images[1][0].image_name == FILE_4_NAME
    # Test non-pds compatible images (FILE_6) are not added to images list
    assert len(test_set.images) == 2
    # Test that next/previous will be enabled
    assert test_set.next_prev_enabled


def test_image_set_next_method():
    """Test the next method & that loops to beginning if at the last image"""
    filepaths = [FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image[0].file_name == FILE_5_NAME
    test_set.next()
    assert test_set.current_image_index == 1
    assert test_set.current_image[0].file_name == FILE_3_NAME
    test_set.next()
    assert test_set.current_image_index == 2
    assert test_set.current_image[0].file_name == FILE_4_NAME
    test_set.next()
    assert test_set.current_image_index == 0
    assert test_set.current_image[0].file_name == FILE_5_NAME


def test_image_set_previous_method():
    """Test the previous method & loops to end if at the first image"""
    filepaths = [FILE_3, FILE_4, FILE_5]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image[0].file_name == FILE_5_NAME
    test_set.previous()
    assert test_set.current_image_index == 2
    assert test_set.current_image[0].file_name == FILE_4_NAME
    test_set.previous()
    assert test_set.current_image_index == 1
    assert test_set.current_image[0].file_name == FILE_3_NAME
    test_set.previous()
    assert test_set.current_image_index == 0
    assert test_set.current_image[0].file_name == FILE_5_NAME


def test_image_set_append_method():
    """Test append method with multiple images"""
    filepaths = [FILE_1]
    new_files = [FILE_2, FILE_3]
    test_set = pdsview.ImageSet(filepaths)
    assert test_set.current_image_index == 0
    assert test_set.current_image[0].file_name == FILE_1_NAME
    assert len(test_set.images) == 1
    assert not(test_set.next_prev_enabled)
    # Mimic how append method is used in pdsview
    first_new_image = len(test_set.images)
    test_set.append(new_files, first_new_image)
    assert test_set.current_image_index == 1
    assert test_set.current_image[0].file_name == FILE_2_NAME
    assert FILE_3_NAME in str(test_set.images)
    assert test_set.next_prev_enabled


def test_ROI_data():
    """Test the ROI_data to cut out the correct region of data"""
    test_set = pdsview.ImageSet([FILE_3])
    width = test_set.current_image[0].width
    height = test_set.current_image[0].height
    test_data_1 = test_set.ROI_data(0, 0, width, height)
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

# TODO test channels when there is a 3 band test image
