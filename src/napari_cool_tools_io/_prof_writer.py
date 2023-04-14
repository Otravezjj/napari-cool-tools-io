import os.path as ospath
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List

from napari.types import FullLayerData
from napari.utils.notifications import show_info
from numpy import flip


def prof_file_writer(path: str, layer_data: list[FullLayerData]) -> List[str]:
    """
    Args:

    Returns:

    """
    for layer in layer_data:
        data, attributes, layer_type = layer

        show_info(
            f"path: {path}, shape: {data.shape}, attributes: {attributes}\n"
        )

        # case .prof files should be 3 dimensional
        if data.ndim == 3:
            dims = data.shape
            valid_meta, meta_path = prof_proc_meta(path)

            if valid_meta is False:
                create_prof_meta(meta_path, dims)

            # reverse flip and transpose that occured upon loading
            save = flip(data, 1).transpose(0, 2, 1)

            save.tofile(path)

            show_info(f"{path} was saved")

            return [path]
        # case data is not proper dimension
        else:
            return None


def create_prof_meta(meta_path, dims):
    """
    Args:
        meta_path(str or list of str): Path to file, or list of paths containing metadata.
        dims(Tuple): (height(int), width(int), length(int))

    Returns:
    """
    num_frames, bscan_width, height = dims
    root = ET.Element("Napari_Metadata")
    meta = ET.SubElement(root, "Metadata")
    vol_size = ET.SubElement(meta, "Volume_Size")
    vol_size.set("Height", str(height))
    vol_size.set("BscanWidth", str(bscan_width))
    vol_size.set("Number_of_Frames", str(num_frames))

    out_tree = ET.ElementTree(root)
    out_tree.write(meta_path)
    show_info(f"New Metadata: {ET.tostring(root)}\nSaved to {meta_path}\n")
    return


def prof_proc_meta(path):
    """Process .prof file xml metadata.

    Args:
        path(str or list of str): Path to file, or list of paths.

    Returns:
        If xml metafile is valid returns tuple(height(int),width(int),depth(int)) else returns None
    """

    height = None
    depth = None
    valid_meta_file_exists = False

    show_info(f"\nChecking file: {path}")

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
    if Path(meta_path).is_file():
        show_info("Meta Data exists.")

        tree = ET.parse(meta_path)
        root = tree.getroot()
        volume_size = root.find(".//Volume_Size").attrib
        height = int(volume_size["Height"])
        width = int(volume_size["BscanWidth"])
        depth = int(volume_size["Number_of_Frames"])

        # Case no valid values obtained from metafile return None
        if depth is not None and height is not None and width is not None:
            valid_meta_file_exists = True
        else:
            pass

        return (valid_meta_file_exists, meta_path)

    # case no metadata request path to metadata or cancel file load
    else:
        return (valid_meta_file_exists, meta_path)
