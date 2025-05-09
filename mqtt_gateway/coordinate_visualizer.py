import numpy as np
import matplotlib.pyplot as plt
from typing import List, Tuple, Optional
from .coordinate_converter import CoordinateConverter


class CoordinateVisualizer:
  def __init__(self, background_image_path: Optional[str] = None):
    """
    Initialize the coordinate visualizer.

    Args:
        background_image_path: Optional path to a background image to display
    """
    self.background_image = None
    if background_image_path:
      self.background_image = plt.imread(background_image_path)

  def _create_grid_points(self, x_range: Tuple[float, float], y_range: Tuple[float, float], 
                        num_points: int = 10) -> List[Tuple[float, float]]:
    """Create a grid of points for visualization."""
    x = np.linspace(x_range[0], x_range[1], num_points)
    y = np.linspace(y_range[1], y_range[0], num_points)  # Reversed for sim coordinates
    return [(xi, yi) for xi in x for yi in y]

  def _plot_axes_and_grid(self, ax, points: List[Tuple[float, float]], 
                        color: str = 'gray', alpha: float = 0.3):
    """Plot coordinate axes and grid lines."""
    # Plot grid points
    ax.scatter(*zip(*points), c=color, alpha=alpha, s=1)
    
    # Plot x and y axes
    x_coords, y_coords = zip(*points)
    min_x, max_x = min(x_coords), max(x_coords)
    min_y, max_y = min(y_coords), max(y_coords)
    
    # X-axis
    ax.plot([min_x, max_x], [0, 0], color=color, alpha=alpha, linestyle='--')
    # Y-axis
    ax.plot([0, 0], [min_y, max_y], color=color, alpha=alpha, linestyle='--')

  def plot_coordinate_transformation(
    self,
    converter: CoordinateConverter,
    source_points: List[Tuple[float, float]],
    target_points: Optional[List[Tuple[float, float]]] = None,
    title: str = "Coordinate Transformation",
    figsize: Tuple[int, int] = (12, 6),
    grid_range: Tuple[Tuple[float, float], Tuple[float, float]] = ((-50, 50), (-50, 50)),
    num_grid_points: int = 10
  ):
    """
    Plot source points and their transformed coordinates with transformed coordinate systems.

    Args:
        converter: CoordinateConverter instance
        source_points: List of points in source coordinate system
        target_points: Optional list of expected target points for verification
        title: Plot title
        figsize: Figure size (width, height)
        grid_range: Range of grid points to plot ((x_min, x_max), (y_min, y_max))
        num_grid_points: Number of grid points in each dimension
    """
    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Create grid points
    grid_points = self._create_grid_points(grid_range[0], grid_range[1], num_grid_points)
    transformed_grid = converter.convert_points(grid_points)

    # Plot source coordinates
    ax1.set_title("Source Coordinates")
    if self.background_image is not None:
      ax1.imshow(self.background_image, 
                extent=[0, self.background_image.shape[1], 
                       self.background_image.shape[0], 0])  # Flipped for sim coordinates
    self._plot_axes_and_grid(ax1, grid_points)
    ax1.scatter(*zip(*source_points), c='blue', label='Source Points')
    ax1.grid(True)
    ax1.legend()

    # Plot target coordinates
    ax2.set_title("Target Coordinates")
    if self.background_image is not None:
      ax2.imshow(self.background_image, 
                extent=[0, self.background_image.shape[1], 
                       self.background_image.shape[0], 0])  # Flipped for sim coordinates
    self._plot_axes_and_grid(ax2, transformed_grid)
    transformed_points = converter.convert_points(source_points)
    ax2.scatter(*zip(*transformed_points), c='red', label='Transformed Points')
    if target_points:
      ax2.scatter(*zip(*target_points), c='green', marker='x', label='Expected Points')
    ax2.grid(True)
    ax2.legend()

    # Add connecting lines between corresponding points
    for src, tgt in zip(source_points, transformed_points):
      ax1.plot([src[0]], [src[1]], 'bo')
      ax2.plot([tgt[0]], [tgt[1]], 'ro')

    plt.suptitle(title)
    plt.tight_layout()
    return fig

  def plot_inverse_transformation(
    self,
    converter: CoordinateConverter,
    target_points: List[Tuple[float, float]],
    source_points: Optional[List[Tuple[float, float]]] = None,
    title: str = "Inverse Coordinate Transformation",
    figsize: Tuple[int, int] = (12, 6),
    grid_range: Tuple[Tuple[float, float], Tuple[float, float]] = ((-50, 50), (-50, 50)),
    num_grid_points: int = 10
  ):
    """
    Plot target points and their inverse transformed coordinates with transformed coordinate systems.

    Args:
        converter: CoordinateConverter instance
        target_points: List of points in target coordinate system
        source_points: Optional list of expected source points for verification
        title: Plot title
        figsize: Figure size (width, height)
        grid_range: Range of grid points to plot ((x_min, x_max), (y_min, y_max))
        num_grid_points: Number of grid points in each dimension
    """
    # Create figure with two subplots side by side
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)

    # Create grid points
    grid_points = self._create_grid_points(grid_range[0], grid_range[1], num_grid_points)
    transformed_grid = converter.convert_points(grid_points)

    # Plot target coordinates
    ax1.set_title("Target Coordinates")
    if self.background_image is not None:
      ax1.imshow(self.background_image, 
                extent=[0, self.background_image.shape[1], 
                       self.background_image.shape[0], 0])  # Flipped for sim coordinates
    self._plot_axes_and_grid(ax1, transformed_grid)
    ax1.scatter(*zip(*target_points), c='red', label='Target Points')
    ax1.grid(True)
    ax1.legend()

    # Plot inverse transformed coordinates
    ax2.set_title("Inverse Transformed Coordinates")
    if self.background_image is not None:
      ax2.imshow(self.background_image, 
                extent=[0, self.background_image.shape[1], 
                       self.background_image.shape[0], 0])  # Flipped for sim coordinates
    self._plot_axes_and_grid(ax2, grid_points)
    inverse_transformed_points = converter.inverse_convert_points(target_points)
    ax2.scatter(*zip(*inverse_transformed_points), c='blue', label='Inverse Transformed Points')
    if source_points:
      ax2.scatter(*zip(*source_points), c='green', marker='x', label='Expected Points')
    ax2.grid(True)
    ax2.legend()

    # Add connecting lines between corresponding points
    for tgt, inv in zip(target_points, inverse_transformed_points):
      ax1.plot([tgt[0]], [tgt[1]], 'ro')
      ax2.plot([inv[0]], [inv[1]], 'bo')

    plt.suptitle(title)
    plt.tight_layout()
    return fig


def main():
  """
  Example usage of the CoordinateVisualizer.
  """
  # Example points in simulation space
  sim_points = [(0, 0), (10, 0), (0, 10), (10, 10), (5, 5)]

  # Create converter with the same parameters as in message_converter.py
  sim_origin = (0, 0)
  sim_unit_ft = 0.784
  sim_unit_m = sim_unit_ft / 3.281

  robots_origin_x = 61.1 / sim_unit_ft
  robots_origin_y = 11.36 / sim_unit_ft
  robots_origin = (robots_origin_x, robots_origin_y)
  robots_unit_m = 1

  converter = CoordinateConverter(
    source_origin=sim_origin,
    target_origin=robots_origin,
    rotation_angle=90,
    scale_factor=robots_unit_m / sim_unit_m,
    reflect_x=False,
    reflect_y=True,
  )

  # Create visualizer (without background image for this example)
  visualizer = CoordinateVisualizer()

  # Plot the transformation
  fig = visualizer.plot_coordinate_transformation(
    converter=converter,
    source_points=sim_points,
    title="Simulation to Robot Space Transformation",
    grid_range=((-20, 20), (-20, 20)),  # Adjust grid range as needed
    num_grid_points=20  # Adjust number of grid points as needed
  )

  # Show the plot
  plt.show()


if __name__ == "__main__":
  main()
