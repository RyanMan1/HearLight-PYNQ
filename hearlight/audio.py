import ipywidgets as widgets
import numpy as np
import traitlets    
import plotly.express as px
import plotly.graph_objs as go
import os

from pynq.lib import MicroblazeRPC

import hearlight
from .css import css

def audio_led_driver_setup(ol):
    """Programmes the microblaze with the LED driver capable of any pattern/LED brightness.
        'ol' is base overlay instance
    """
    lib_path = os.path.dirname(hearlight.__file__)
    c_src_path = os.path.join(lib_path, 'driver/driver.c')

    with open(c_src_path, 'r') as f:
        led_driver_source = f.read()

    return MicroblazeRPC(ol.iop_arduino, led_driver_source)
    

"""Class for audio control panel

"""
class AudioControlPanel(traitlets.HasTraits):
    fs_trait = traitlets.Int()
    n_samples_plot_trait = traitlets.Int()
    
    def __init__(self, *audio_processors):
        # text entry for audio sample frequency
        self.fs_entry = widgets.IntText(value=48000, disabled=False, layout = {'width' : '100%'})
        traitlets.link((self.fs_entry, 'value'), (self, 'fs_trait'))
                
        # button to start audio stream and device control
        self.start_button = widgets.Button(description='START', icon='play')
        self.start_button.add_class('start_button')

        # button to stop audio stream and device control
        self.stop_button = widgets.Button(description='STOP', icon='stop')
        self.stop_button.add_class('stop_button')
        
        ## audio plots settings
        # number of time samples to show on plot
        self.n_samples_plot_entry = widgets.IntText(value=20480, disabled=False, layout = {'width' : '100%'})
        traitlets.link((self.n_samples_plot_entry, 'value'), (self, 'n_samples_plot_trait'))
        self.observe(self._setup_plots, ['n_samples_plot_trait'])
        
        # toggle button to pause/resume time domain plot update
        self.time_plot_pause_toggle = widgets.ToggleButton(description='Pause time domain plot update', icon='pause', layout = {'width' : '250px'}, value = True)
        self.time_plot_pause_toggle.add_class('time_plot_pause_toggle')
        
        # toggle button to pause/resume freq domain plot update
        self.freq_plot_pause_toggle = widgets.ToggleButton(description='Pause frequency domain plot update', icon='pause', layout = {'width' : '250px'}, value = True)
        self.freq_plot_pause_toggle.add_class('freq_plot_pause_toggle')

        # PLOTS SETUP
        # time domain plot
        plot_data = np.zeros(self.n_samples_plot_trait)
        line = px.line(x = np.arange(0, self.n_samples_plot_trait, 1),
                       y = plot_data)
        self.fig = go.FigureWidget(line, layout = go.Layout(xaxis = {'title' : 'sample'},
                                              yaxis = {'title' : 'amplitude'}))
        self.fig_ft = go.FigureWidget()

        self.processor_settings = {}
        
        for audio_processor in audio_processors:
            self.processor = audio_processor(self)
        
        self._setup_plots(0)
        self._layout_panel()
                
    def _layout_panel(self):
        ### audio control panel box
        self.audio_control_panel = widgets.Box()
        self.audio_control_panel.add_class('audio_control_panel')
        self.audio_control_panel.children += (widgets.HTML(value=css),)
        
        ## audio setup box (start/stop button and parameters)
        audio_setup_box = widgets.Box()
        audio_setup_box.add_class('audio_setup_box')
        audio_setup_box_heading = widgets.HTML(value='<b>&nbsp;Audio setup</b>')
        audio_setup_box_heading.add_class('section_heading')
        audio_setup_box.children += (audio_setup_box_heading,)
        self.audio_control_panel.children += (audio_setup_box,)
        
        # audio setup buttons box (start/stop)
        audio_setup_buttons_box = widgets.Box()
        audio_setup_buttons_box.add_class('audio_setup_buttons_box')
        audio_setup_buttons_box.children += (self.start_button, self.stop_button, )
        audio_setup_box.children += (audio_setup_buttons_box,)
        
        # audio setup parameters box (n_fft_bins etc)
        audio_setup_parameters_box = widgets.Box()
        audio_setup_parameters_box.add_class('audio_setup_parameters_box')
        
        # place all setup parameters boxes into a tuple
        fs_entry_box = widgets.Box()
        fs_entry_box.add_class('label_setting_box')
        fs_entry_box.children += (widgets.HTML(value=f"<font color='black'>Audio sample frequency (Hz): "), self.fs_entry, )
        audio_setup_parameters = ()
        audio_setup_parameters += (fs_entry_box, )
        
        # add inherited settings
        for label, widget in self.processor_settings.items():
            box = widgets.Box()
            box.add_class('label_setting_box')
            box.children += (widgets.HTML(value=f"<font color='blue'>{label}"), widget, )
            audio_setup_parameters += (box, )

        audio_setup_parameters_box.children += audio_setup_parameters
        audio_setup_box.children += (audio_setup_parameters_box,)
        
        # audio plot settings box
        audio_plots_settings_box = widgets.Box()
        audio_plots_settings_box.add_class('audio_plots_settings_box')
        audio_plots_settings_box
        
        n_samples_plot_entry_box = widgets.Box()
        n_samples_plot_entry_box.add_class('label_setting_box')
        n_samples_plot_entry_box.children += (widgets.Label('Number of samples on plot: '), self.n_samples_plot_entry, )
        
        time_plot_pause_toggle_box = widgets.Box()
        time_plot_pause_toggle_box.children += (self.time_plot_pause_toggle,)
        
        freq_plot_pause_toggle_box = widgets.Box()
        freq_plot_pause_toggle_box.children += (self.freq_plot_pause_toggle,)
        
        audio_plots_settings = (n_samples_plot_entry_box,
                                time_plot_pause_toggle_box,
                                freq_plot_pause_toggle_box,)
        audio_plots_settings_box.children += audio_plots_settings
        audio_setup_box.children += (audio_plots_settings_box,)
        
        # audio setup info box
        audio_setup_info_box = widgets.Box()
        audio_setup_info_box.add_class('audio_setup_info_box')
        audio_setup_box.children += (audio_setup_info_box,)
        
        ## audio plots box (audio stream/FFT or spectrogram later... and buttons to disable plot updates)
        audio_plots_box = widgets.Box()
        audio_plots_box.add_class('audio_plots_box')
        audio_plots_box_heading = widgets.HTML(value='<b>&nbsp;Audio plots</b>')
        audio_plots_box_heading.add_class('section_heading')
        audio_plots_box.children += (audio_plots_box_heading,)
        self.audio_control_panel.children += (audio_plots_box,)
                
        # audio plots time domain plot
        time_plot_box = widgets.Box()
        time_plot_box.add_class('plot_box')
        time_plot_box.children += (self.fig,)
        audio_plots_box.children += (time_plot_box,)        
        
        # audio plots freq domain plot
        freq_plot_box = widgets.Box()
        freq_plot_box.add_class('plot_box')
        freq_plot_box.children += (self.fig_ft,)
        audio_plots_box.children += (freq_plot_box,)
        
    def _setup_plots(self, trait_change):
        # time domain plot
        plot_data = np.zeros(self.n_samples_plot_trait)
        self.fig.data[0].update({'x' : np.arange(0, self.n_samples_plot_trait, 1)})
        self.fig.data[0].update({'y' : plot_data})
        
        self.fig.update_layout(xaxis = {'title' : 'sample index'})
        self.fig.update_layout(yaxis = {'title' : 'amplitude'})
        self.fig.update_layout(title = {'text' : 'Audio signal in time domain'})

        # MAKE THIS MORE DETERMINISTIC....
        self.fig.update_yaxes(
            range=(-100000, 100000),
            constrain='domain'
        )
        