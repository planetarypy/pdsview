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
