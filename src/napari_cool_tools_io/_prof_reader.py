import os
import os.path as ospath
import xml.etree.ElementTree as ET
from pathlib import Path

import numpy as np
from napari.utils.notifications import show_info

data_element_size = 4  # number of bytes per data element f32 == 4 bytes


def prof_get_reader(path):
    """Reader for COOL lab .prof file format.

    Args:
        path(str or list of str): Path to file, or list of paths.

    Returns:
        function or None
        If the path is a recognized format, return a function that accepts the
        same path or list of paths, and returns a list of layer data tuples.
    """
    # If format is recogized return reader function
    if isinstance(path, str) and path.endswith(".prof"):
        # calculate file size in bytes
        file_size = os.path.getsize(path)

        # calculate number of data entries
        # in this case we are using 32 bit floating point
        # aka 4 bytes  as there are 8 bits per byte
        num_entries = file_size / data_element_size

        meta = prof_proc_meta(path)

        # case meta data is valid
        if meta is not None:
            print(
                f"h,w,d {meta}, size(bytes): {file_size}, data entries: {num_entries}"
            )
            # calculate width of data volume using height and depth info
            # from meta data file and calculated number of data entries
            h, w, d = meta

            globals()["prof_width"] = w
            globals()["prof_height"] = h
            globals()["prof_depth"] = d

        # case meta data is not valid
        else:
            return None

        return prof_file_reader
    return None


def prof_proc_meta(path):
    """Process .prof file xml metadata.

    Args:
        path(str or list of str): Path to file, or list of paths.

    Returns:
        If xml metafile is valid returns tuple(height(int),width(int),depth(int)) else returns None
    """

    height = None
    depth = None

    show_info(f"\nOpening file: {path}")

    head, tail = ospath.split(path)

    # isolate file name from path and .prof extension
    # file_name = ospath.basename(path)
    file_name = tail

    # remove .prof extenstion
    file_no_ext = file_name.replace(".prof", "")

    # remove common .prof specifiers _OCTA and _Struc
    file_base = file_no_ext.replace("_OCTA", "").replace("_Struc", "")

    # constuct path to metafile assumed to be in same directory
    meta_path = ospath.join(head, file_base + ".xml")
    show_info(f"Associated meta data file: {meta_path}")

    # verify whether meta file exists or not
    # if isinstance(meta_path, str):
    if Path(meta_path).is_file():
        show_info("Meta Data exists:")

        tree = ET.parse(meta_path)
        root = tree.getroot()
        volume_size = root.find(".//Volume_Size").attrib
        height = int(volume_size["Height"])
        width = int(volume_size["BscanWidth"])
        depth = int(volume_size["Number_of_Frames"])

        # Case no valid values obtained from metafile return None
        if depth is not None and height is not None and width is not None:
            return (height, width, depth)
        else:
            return None

    # case no metadata request path to metadata or cancel file load
    else:
        return None


def prof_file_reader(path):
    """Take a path or list of paths to .prof files and return a list of LayerData tuples.

    Args:
        path(str or list of str): Path to file, or list of paths.

    Returns:
        layer_data : list of tuples
            A list of LayerData tuples where each tuple in the list contains
            (data, metadata, layer_type), where data is a numpy array, metadata is
            a dict of keyword arguments for the corresponding viewer.add_* method
            in napari, and layer_type is a lower-case string naming the type of
            layer. Both "meta", and "layer_type" are optional. napari will
            default to layer_type=="image" if not provided
    """

    h = globals()["prof_height"]
    w = globals()["prof_width"]

    # isolate file name from path and .prof extension
    # file_name = ospath.basename(path)
    head, tail = ospath.split(path)
    file_name = tail.replace(".", "_")

    # define chuncks as little endian f32 4 byte floats with HEIGHT values
    # per row and WIDTH values per column
    dot_prof = np.dtype(("<f4", (h, w)))

    # generate numpy array by loading 400 * 496 * f32 sized data chunks
    # and stacking them until end of file is reached
    b_scan = np.fromfile(path, dtype=dot_prof, count=-1)

    # transpose array so that x and y are switched then flip array
    # to better orient b-scans for manual segmentation
    display = b_scan.transpose(0, 2, 1)
    # display = display[:,::-1,:]
    display = np.flip(b_scan.transpose(0, 2, 1), 1)
    # display = b_scan

    # optional kwargs for viewer.add_* method
    add_kwargs = {"name": file_name}

    # optional layer type argument
    layer_type = "image"

    show_info(
        f"layer_name: {file_name}, shape: {display.shape}, dtype: {display.dtype}, layer type: {layer_type}\n"
    )
    return [(display, add_kwargs, layer_type)]
