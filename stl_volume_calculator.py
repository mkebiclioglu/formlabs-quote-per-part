import trimesh

def calculate_stl_volume(stl_file_path, units='mm'):
    """
    Calculate the volume of an STL file in cubic centimeters.

    Args:
        stl_file_path (str): Path to the STL file
        units (str): 'mm', 'cm', or 'inches' — assumed input units

    Returns:
        float: Volume in cubic centimeters
    """
    print(f"Debug: Function called with units={units}")  # Debug print
    try:
        mesh = trimesh.load(stl_file_path, force='mesh')
        print(f"Debug: Mesh loaded successfully")  # Debug print

        if not isinstance(mesh, trimesh.Trimesh):
            raise ValueError("Loaded file is not a valid mesh.")

        # Fix mesh if needed
        if not mesh.is_watertight:
            print("Warning: Mesh is not watertight, volume may be inaccurate.")
            mesh.fix_normals()

        # Convert units if needed
        if units == 'inches':
            mesh.apply_scale(25.4)  # convert to mm
        elif units == 'cm':
            mesh.apply_scale(10.0)  # convert to mm

        volume_mm3 = mesh.volume
        volume_cm3 = volume_mm3 / 1000.0
        print(f"Debug: Volume calculated: {volume_cm3} cm³")  # Debug print

        if volume_cm3 <= 0:
            raise ValueError("Calculated volume is zero or negative.")

        return volume_cm3

    except Exception as e:
        print(f"Debug: Error occurred: {str(e)}")  # Debug print
        raise Exception(f"Error calculating STL volume: {str(e)}")
