import numpy as np
from PIL import Image, ImageDraw, ImageFont
import random
import math
import io

def split_image(image, num_pieces=8, total_fragments=100, bg_color='white', invert_colors=False):
    """
    Split an image into multiple fragments using Voronoi diagram-like patterns.
    
    Parameters:
    - image: PIL Image object
    - num_pieces: Number of output images to generate
    - total_fragments: Total number of fragments to split the image into
    - bg_color: Background color ('white', 'black', or 'transparent')
    - invert_colors: Whether to invert colors of the fragments
    
    Returns:
    - List of PIL Image objects containing the split images
    """
    width, height = image.width, image.height
    
    # Convert image to numpy array for easier pixel manipulation
    img_array = np.array(image)
    
    # Generate fragment masks
    fragment_masks = generate_simple_fragments(width, height, num_pieces, total_fragments)
    
    # Create split images
    result_images = []
    for i, mask_info in enumerate(fragment_masks):
        mask, fragment_count = mask_info['mask'], mask_info['fragment_count']
        
        # Create split image from fragments
        split_img = create_split_image(image, mask, invert_colors, bg_color)
        
        result_images.append({
            'image': split_img,
            'fragment_count': fragment_count
        })
    
    return result_images

def generate_simple_fragments(width, height, num_pieces, total_fragments):
    """
    Generate fragment masks using Voronoi diagram.
    
    Returns a list of masks, where each mask is a numpy array with values 
    indicating which fragment each pixel belongs to.
    """
    # Create a main mask array - shows which fragment each pixel is assigned to
    main_mask = np.zeros((height, width), dtype=np.uint8)
    
    # Calculate fragments per piece - try to distribute evenly
    fragments_per_piece = total_fragments // num_pieces
    remaining_fragments = total_fragments % num_pieces
    
    # Assign fragments to each piece
    fragment_assignments = []
    for i in range(num_pieces):
        current_fragments = fragments_per_piece
        if remaining_fragments > 0:
            current_fragments += 1
            remaining_fragments -= 1
        fragment_assignments.append(current_fragments)
    
    # Step 1: Generate seed points using Poisson disk sampling
    seeds = generate_poisson_points(width, height, total_fragments)
    
    # Step 2: Use Voronoi diagram to assign each pixel to its nearest seed
    for y in range(height):
        for x in range(width):
            min_dist = float('inf')
            nearest_seed = -1
            
            # Find the nearest seed point
            for i, seed in enumerate(seeds):
                dist = math.sqrt((x - seed[0])**2 + (y - seed[1])**2)
                if dist < min_dist:
                    min_dist = dist
                    nearest_seed = i
            
            # Assign pixel to the found fragment (fragment IDs start at 1)
            main_mask[y, x] = nearest_seed + 1
    
    # Step 3: Randomly assign fragments to different images
    # Create an array with all fragment IDs
    fragment_ids = list(range(1, len(seeds) + 1))
    
    # Shuffle fragment IDs randomly
    random.shuffle(fragment_ids)
    
    # Create masks for each image - containing only fragments assigned to that image
    image_masks = []
    fragment_id_index = 0
    
    for piece_index in range(num_pieces):
        fragment_count = fragment_assignments[piece_index]
        piece_mask = np.zeros((height, width), dtype=np.uint8)
        
        # Collect fragment IDs for current image
        current_piece_fragment_ids = []
        for i in range(fragment_count):
            if fragment_id_index < len(fragment_ids):
                current_piece_fragment_ids.append(fragment_ids[fragment_id_index])
                fragment_id_index += 1
        
        # Fill selected fragments into current image mask
        for y in range(height):
            for x in range(width):
                fragment_id = main_mask[y, x]
                if fragment_id in current_piece_fragment_ids:
                    # Assign a new local fragment ID (1 to fragment_count)
                    piece_mask[y, x] = current_piece_fragment_ids.index(fragment_id) + 1
        
        # Add current image mask to results
        image_masks.append({
            'mask': piece_mask,
            'fragment_count': fragment_count
        })
    
    return image_masks

def generate_poisson_points(width, height, num_points):
    """
    Generate randomly distributed points using a simplified Poisson disk sampling.
    """
    points = []
    min_distance = math.sqrt((width * height) / (num_points * 2))  # Estimated minimum distance
    
    # Generate points in a grid to ensure better distribution
    grid_size = math.ceil(math.sqrt(num_points))
    cell_width = width / grid_size
    cell_height = height / grid_size
    
    # Place one random point in each grid cell
    for gy in range(grid_size):
        for gx in range(grid_size):
            if len(points) >= num_points:
                break
                
            # Choose a random point within the grid cell
            px = gx * cell_width + random.random() * cell_width
            py = gy * cell_height + random.random() * cell_height
            
            # Add jitter for more irregularity
            jitter = min_distance * 0.5
            jx = (random.random() * 2 - 1) * jitter
            jy = (random.random() * 2 - 1) * jitter
            
            x = max(0, min(width - 1, px + jx))
            y = max(0, min(height - 1, py + jy))
            
            points.append((x, y))
    
    # Add extra points if needed
    while len(points) < num_points:
        x = random.random() * width
        y = random.random() * height
        
        # Check distance to existing points
        too_close = False
        for point in points:
            dist = math.sqrt((x - point[0])**2 + (y - point[1])**2)
            if dist < min_distance * 0.5:
                too_close = True
                break
        
        if not too_close:
            points.append((x, y))
    
    return points[:num_points]

def create_split_image(source_img, fragment_mask, should_invert, bg_color):
    """
    Create a split image from fragment mask.
    """
    width, height = source_img.width, source_img.height
    
    # Create a new image with the specified background color
    if bg_color == 'transparent':
        result_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    elif bg_color == 'black':
        result_img = Image.new('RGB', (width, height), (0, 0, 0))
    else:  # default to white
        result_img = Image.new('RGB', (width, height), (255, 255, 255))
    
    # Get source image pixel data
    source_array = np.array(source_img)
    has_transparency = source_img.mode == 'RGBA'
    
    # Create result image pixel data
    result_array = np.array(result_img)
    
    # Copy all fragment pixels
    for y in range(height):
        for x in range(width):
            if fragment_mask[y, x] > 0:  # If pixel belongs to any fragment
                if bg_color == 'transparent' and has_transparency:
                    # For transparent background with RGBA image
                    result_array[y, x] = source_array[y, x]
                    # If source pixel is completely transparent, keep it transparent
                    if has_transparency and source_array[y, x, 3] == 0:
                        result_array[y, x, 3] = 0
                    else:
                        result_array[y, x, 3] = 255  # Make fully opaque
                else:
                    # For RGB images or non-transparent backgrounds
                    if has_transparency:
                        # Copy RGB channels, ignore alpha
                        result_array[y, x, 0:3] = source_array[y, x, 0:3]
                    else:
                        result_array[y, x] = source_array[y, x]
    
    # Invert colors if requested
    if should_invert:
        if bg_color == 'transparent':
            # Only invert non-transparent areas
            mask = result_array[:, :, 3] > 0
            result_array[mask, 0:3] = 255 - result_array[mask, 0:3]
        else:
            # Create a mask of fragment areas
            mask = fragment_mask > 0
            result_array[mask] = 255 - result_array[mask]
    
    # Convert array back to image
    if bg_color == 'transparent':
        result_img = Image.fromarray(result_array, 'RGBA')
    else:
        result_img = Image.fromarray(result_array, 'RGB')
    
    return result_img


def save_split_images(split_images, original_filename, bg_color='white'):
    """
    Save split images to files and return file paths.
    
    Parameters:
    - split_images: List of dictionaries containing image and fragment_count
    - original_filename: Original filename to use as base for new filenames
    - bg_color: Background color used (determines image format)
    
    Returns:
    - List of file paths
    """
    file_paths = []
    base_filename = original_filename.split('.')[0]
    
    for i, img_data in enumerate(split_images):
        img = img_data['image']
        fragment_count = img_data['fragment_count']
        
        # Determine format based on background color
        format_ext = 'png' if bg_color == 'transparent' else 'jpg'
        output_filename = f"{base_filename}_fragment{i+1}_pieces{fragment_count}.{format_ext}"
        
        # Save the image
        img.save(output_filename, quality=95)
        file_paths.append(output_filename)
    
    return file_paths

# Example usage:
if __name__ == "__main__":
    # Load an image
    image_path = "a.jpg"
    try:
        img = Image.open(image_path)
        
        # Split the image
        split_results = split_image(
            img, 
            num_pieces=10,            # Number of output images
            total_fragments=100,     # Total number of fragments
            bg_color='black',        # Background color ('white', 'black', or 'transparent')
            invert_colors=True      # Whether to invert colors
        )
        
        # Save the split images
        save_split_images(split_results, image_path)
        
        print(f"Split into {len(split_results)} images")
        for i, result in enumerate(split_results):
            print(f"Image {i+1}: {result['fragment_count']} fragments")
            
    except Exception as e:
        print(f"Error processing image: {e}")