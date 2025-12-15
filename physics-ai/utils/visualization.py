# utils/visualization.py
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Any, Optional
import matplotlib.animation as animation
from mpl_toolkits.mplot3d import Axes3D

class PhysicsVisualizer:
    def __init__(self):
        self.fig_size = (10, 8)
        self.dpi = 100
        
    def create_projectile_trajectory(self, result_data: Dict[str, float], 
                                   params: Dict[str, float] = None) -> go.Figure:
        """Create interactive 3D projectile trajectory"""
        
        # Extract parameters
        if params:
            v0 = params.get('initial_velocity', 20)
            angle = params.get('angle', 45)
            height = params.get('height', 0)
        else:
            # Back-calculate from results
            range_val = result_data.get('range', 40)
            time_flight = result_data.get('time_flight', 4)
            v0 = range_val / (time_flight * np.cos(np.radians(45)))
            angle = 45
            height = 0
        
        # Generate trajectory points
        t = np.linspace(0, result_data.get('time_flight', 4), 100)
        
        # Kinematic equations
        x = v0 * np.cos(np.radians(angle)) * t
        y = v0 * np.sin(np.radians(angle)) * t - 0.5 * 9.81 * t**2 + height
        
        # Create 3D trajectory
        fig = go.Figure()
        
        # Main trajectory
        fig.add_trace(go.Scatter3d(
            x=x, y=np.zeros_like(x), z=y,
            mode='lines',
            line=dict(color='blue', width=6),
            name='Trajectory',
            hovertemplate='Distance: %{x:.1f}m<br>Height: %{z:.1f}m<extra></extra>'
        ))
        
        # Launch point
        fig.add_trace(go.Scatter3d(
            x=[0], y=[0], z=[height],
            mode='markers',
            marker=dict(size=12, color='green', symbol='circle'),
            name='Launch Point'
        ))
        
        # Landing point
        fig.add_trace(go.Scatter3d(
            x=[x[-1]], y=[0], z=[0],
            mode='markers',
            marker=dict(size=12, color='red', symbol='x'),
            name='Landing Point'
        ))
        
        # Maximum height point
        max_height_idx = np.argmax(y)
        fig.add_trace(go.Scatter3d(
            x=[x[max_height_idx]], y=[0], z=[y[max_height_idx]],
            mode='markers',
            marker=dict(size=10, color='orange', symbol='diamond'),
            name='Max Height'
        ))
        
        # Ground plane
        ground_x = np.linspace(0, max(x), 10)
        ground_y = np.linspace(-max(x)*0.1, max(x)*0.1, 10)
        ground_X, ground_Y = np.meshgrid(ground_x, ground_y)
        ground_Z = np.zeros_like(ground_X)
        
        fig.add_trace(go.Surface(
            x=ground_X, y=ground_Y, z=ground_Z,
            opacity=0.3,
            colorscale='Greys',
            showscale=False,
            name='Ground'
        ))
        
        # Update layout
        fig.update_layout(
            title=f'Projectile Motion: v₀={v0:.1f} m/s, θ={angle}°',
            scene=dict(
                xaxis_title='Distance (m)',
                yaxis_title='Width (m)', 
                zaxis_title='Height (m)',
                camera=dict(eye=dict(x=1.5, y=1.5, z=1.2)),
                aspectmode='manual',
                aspectratio=dict(x=2, y=1, z=1)
            ),
            width=800,
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_pendulum_animation(self, result_data: Dict[str, float],
                                params: Dict[str, float] = None) -> go.Figure:
        """Create animated pendulum visualization"""
        
        length = params.get('length', 1.0) if params else 1.0
        period = result_data.get('period_accurate', 2.0)
        max_angle = params.get('max_angle', 30) if params else 30
        
        # Generate motion data
        t = np.linspace(0, 2*period, 200)
        angles = max_angle * np.cos(2 * np.pi * t / period)
        
        # Convert to cartesian coordinates
        x_positions = length * np.sin(np.radians(angles))
        y_positions = -length * np.cos(np.radians(angles))
        
        # Create base figure
        fig = go.Figure()
        
        # Pendulum path (full arc)
        path_angles = np.linspace(-max_angle, max_angle, 100)
        path_x = length * np.sin(np.radians(path_angles))
        path_y = -length * np.cos(np.radians(path_angles))
        
        fig.add_trace(go.Scatter(
            x=path_x, y=path_y,
            mode='lines',
            line=dict(color='lightgray', width=2, dash='dash'),
            name='Pendulum Path',
            showlegend=False
        ))
        
        # Pivot point
        fig.add_trace(go.Scatter(
            x=[0], y=[0],
            mode='markers',
            marker=dict(size=15, color='black', symbol='x'),
            name='Pivot Point'
        ))
        
        # Create frames for animation
        frames = []
        for i in range(len(t)):
            frame = go.Frame(
                data=[
                    # String
                    go.Scatter(
                        x=[0, x_positions[i]],
                        y=[0, y_positions[i]],
                        mode='lines',
                        line=dict(color='brown', width=4),
                        name='String'
                    ),
                    # Bob
                    go.Scatter(
                        x=[x_positions[i]],
                        y=[y_positions[i]],
                        mode='markers',
                        marker=dict(size=20, color='red'),
                        name='Bob'
                    ),
                    # Motion trail
                    go.Scatter(
                        x=x_positions[max(0, i-20):i+1],
                        y=y_positions[max(0, i-20):i+1],
                        mode='markers',
                        marker=dict(size=3, color='red', opacity=0.3),
                        name='Motion Trail',
                        showlegend=False
                    )
                ],
                name=f'frame{i}'
            )
            frames.append(frame)
        
        # Add initial frame
        fig.add_trace(go.Scatter(
            x=[0, x_positions[0]], y=[0, y_positions[0]],
            mode='lines',
            line=dict(color='brown', width=4),
            name='String'
        ))
        fig.add_trace(go.Scatter(
            x=[x_positions[0]], y=[y_positions[0]],
            mode='markers',
            marker=dict(size=20, color='red'),
            name='Bob'
        ))
        
        # Add frames to figure
        fig.frames = frames
        
        # Add animation buttons
        fig.update_layout(
            updatemenus=[{
                'type': 'buttons',
                'showactive': False,
                'buttons': [
                    {
                        'label': 'Play',
                        'method': 'animate',
                        'args': [None, {
                            'frame': {'duration': 50, 'redraw': True},
                            'fromcurrent': True,
                            'mode': 'immediate'
                        }]
                    },
                    {
                        'label': 'Pause',
                        'method': 'animate',
                        'args': [[None], {
                            'frame': {'duration': 0, 'redraw': False},
                            'mode': 'immediate',
                            'transition': {'duration': 0}
                        }]
                    }
                ]
            }],
            title=f'Pendulum Motion: L={length}m, T={period:.2f}s',
            xaxis_title='Position (m)',
            yaxis_title='Height (m)',
            xaxis=dict(range=[-length*1.2, length*1.2], scaleanchor='y'),
            yaxis=dict(range=[-length*1.2, length*0.2]),
            width=600,
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_collision_diagram(self, before_data: Dict, after_data: Dict) -> go.Figure:
        """Create before/after collision visualization"""
        
        fig = go.Figure()
        
        # Before collision
        fig.add_trace(go.Scatter(
            x=[0, 2], y=[1, 1],
            mode='markers+text',
            marker=dict(size=[before_data.get('mass1', 1)*20, before_data.get('mass2', 1)*20],
                       color=['blue', 'red']),
            text=[f"m₁={before_data.get('mass1', 1)}kg<br>v₁={before_data.get('velocity1', 0)}m/s",
                  f"m₂={before_data.get('mass2', 1)}kg<br>v₂={before_data.get('velocity2', 0)}m/s"],
            textposition="middle center",
            name='Before Collision'
        ))
        
        # After collision  
        fig.add_trace(go.Scatter(
            x=[0, 2], y=[0, 0],
            mode='markers+text',
            marker=dict(size=[after_data.get('mass1', 1)*20, after_data.get('mass2', 1)*20],
                       color=['lightblue', 'pink']),
            text=[f"m₁={after_data.get('mass1', 1)}kg<br>v₁'={after_data.get('velocity1', 0):.1f}m/s",
                  f"m₂={after_data.get('mass2', 1)}kg<br>v₂'={after_data.get('velocity2', 0):.1f}m/s"],
            textposition="middle center",
            name='After Collision'
        ))
        
        # Velocity arrows
        # Before collision arrows
        if before_data.get('velocity1', 0) != 0:
            fig.add_annotation(
                x=0, y=1, ax=0.5*before_data.get('velocity1', 0), ay=1,
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='blue'
            )
        if before_data.get('velocity2', 0) != 0:
            fig.add_annotation(
                x=2, y=1, ax=2+0.5*before_data.get('velocity2', 0), ay=1,
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='red'
            )
        
        # After collision arrows
        if after_data.get('velocity1', 0) != 0:
            fig.add_annotation(
                x=0, y=0, ax=0.5*after_data.get('velocity1', 0), ay=0,
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='lightblue'
            )
        if after_data.get('velocity2', 0) != 0:
            fig.add_annotation(
                x=2, y=0, ax=2+0.5*after_data.get('velocity2', 0), ay=0,
                arrowhead=2, arrowsize=1, arrowwidth=2, arrowcolor='pink'
            )
        
        fig.update_layout(
            title='Collision Analysis',
            xaxis_title='Position',
            yaxis_title='Time',
            yaxis=dict(tickvals=[0, 1], ticktext=['After', 'Before']),
            width=800,
            height=400,
            showlegend=True
        )
        
        return fig
    
    def create_force_diagram(self, objects: List[Dict], forces: List[Dict]) -> go.Figure:
        """Create free body diagram"""
        
        fig = go.Figure()
        
        for i, obj in enumerate(objects):
            # Draw object
            fig.add_trace(go.Scatter(
                x=[obj.get('x', 0)], y=[obj.get('y', 0)],
                mode='markers+text',
                marker=dict(size=30, color=f'C{i}'),
                text=[f"{obj.get('name', f'Object {i}')}"],
                textposition="middle center",
                name=obj.get('name', f'Object {i}')
            ))
            
            # Draw forces on this object
            obj_forces = [f for f in forces if f.get('object') == i]
            for force in obj_forces:
                # Force arrow
                fig.add_annotation(
                    x=obj.get('x', 0), y=obj.get('y', 0),
                    ax=obj.get('x', 0) + force.get('fx', 0) * 0.1,
                    ay=obj.get('y', 0) + force.get('fy', 0) * 0.1,
                    arrowhead=2, arrowsize=1, arrowwidth=3,
                    arrowcolor=force.get('color', 'black'),
                    text=f"{force.get('name', 'Force')}<br>{force.get('magnitude', 0):.1f}N"
                )
        
        fig.update_layout(
            title='Free Body Diagram',
            xaxis_title='Position (m)',
            yaxis_title='Position (m)',
            width=600,
            height=600,
            showlegend=True
        )
        
        return fig
    
    def create_energy_diagram(self, energy_data: Dict[str, List[float]], 
                            time_data: List[float]) -> go.Figure:
        """Create energy vs time plot"""
        
        fig = go.Figure()
        
        # Kinetic energy
        if 'kinetic' in energy_data:
            fig.add_trace(go.Scatter(
                x=time_data, y=energy_data['kinetic'],
                mode='lines', name='Kinetic Energy',
                line=dict(color='red', width=3)
            ))
        
        # Potential energy
        if 'potential' in energy_data:
            fig.add_trace(go.Scatter(
                x=time_data, y=energy_data['potential'],
                mode='lines', name='Potential Energy',
                line=dict(color='blue', width=3)
            ))
        
        # Total energy
        if 'total' in energy_data:
            fig.add_trace(go.Scatter(
                x=time_data, y=energy_data['total'],
                mode='lines', name='Total Energy',
                line=dict(color='green', width=3, dash='dash')
            ))
        
        fig.update_layout(
            title='Energy Conservation',
            xaxis_title='Time (s)',
            yaxis_title='Energy (J)',
            width=800,
            height=500,
            showlegend=True
        )
        
        return fig
    
    def create_motion_plot(self, position_data: List[float], 
                          velocity_data: List[float],
                          acceleration_data: List[float],
                          time_data: List[float]) -> go.Figure:
        """Create position, velocity, acceleration vs time plot"""
        
        fig = go.Figure()
        
        # Position
        fig.add_trace(go.Scatter(
            x=time_data, y=position_data,
            mode='lines', name='Position',
            line=dict(color='blue', width=2),
            yaxis='y'
        ))
        
        # Velocity
        fig.add_trace(go.Scatter(
            x=time_data, y=velocity_data,
            mode='lines', name='Velocity',
            line=dict(color='red', width=2),
            yaxis='y2'
        ))
        
        # Acceleration
        fig.add_trace(go.Scatter(
            x=time_data, y=acceleration_data,
            mode='lines', name='Acceleration',
            line=dict(color='green', width=2),
            yaxis='y3'
        ))
        
        # Layout with multiple y-axes
        fig.update_layout(
            title='Motion Analysis',
            xaxis_title='Time (s)',
            yaxis=dict(title='Position (m)', side='left'),
            yaxis2=dict(title='Velocity (m/s)', side='right', overlaying='y'),
            yaxis3=dict(title='Acceleration (m/s²)', side='right', overlaying='y', position=0.95),
            width=800,
            height=500,
            showlegend=True
        )
        
        return fig