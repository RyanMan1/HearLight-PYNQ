import ipywidgets as widgets
import numpy as np
import functools
import asyncio
import traitlets
from time import sleep
import os

from .audio import AudioControlPanel
from .css import css, REQUIRED_CURRENTS_HEIGHT, REQUIRED_CURRENTS_WIDTH, CHANNEL_CURRENTS_HEIGHT, CHANNEL_CURRENTS_WIDTH, ACTUAL_IRRADIANCES_HEIGHT, ACTUAL_IRRADIANCES_WIDTH

from pynq import Overlay
from .driver import ControlLEDs
import hearlight

import copy

N_SWITCHES = 10
N_CHANNELS = 10

OVERLAYS = {'Base overlay' : 'base.bit',
            'Ryan overlay 1' : './overlays/test.bit'}

"""Class for banner panel

"""
class BannerPanel():
    def __init__(self):
        self.banner_image_box = widgets.Box()
        lib_path = os.path.dirname(hearlight.__file__)
        image_path = os.path.join(lib_path, 'images/banner.png')
        banner_image = widgets.Image(value=open(image_path, 'rb').read())
        banner_image.add_class('banner_image_css')
        self.banner_image_box.children += (banner_image,)
        self.banner_image_box.add_class('banner_image_box_css')

"""Class for info panel

"""
class InfoPanel():
    def __init__(self):
        self.info_panel = widgets.VBox()
        self.info_panel.add_class('info_panel_css')
        text_title = widgets.HTML(value='<h1 style="font-size:1.7em"><b>HearLight PYNQ control system</b></h1>')
        text_title.add_class('text_coloured_css')
        text_version_author = widgets.HTML(value='<h2 style="font-size:1em"><i>Version 1.0, December 2022<br><br>Ryan Greer<br>University of Strathclyde</i></h2>')
        text_version_author.add_class('text_css')
        self.info_panel.children += (text_title,
                              text_version_author,)

"""Class for the main control/setup panel.

"""
class MainControlPanel(traitlets.HasTraits):
    device_trait = traitlets.Int()
    shield_trait = traitlets.Int()
    led_max_current_trait = traitlets.Float()
    channel_max_current_trait = traitlets.Float()
    switch_max_current_trait = traitlets.Float()
    device_max_current_trait = traitlets.Float()
    dac_ref_trait = traitlets.Float()
    irr_to_current_trait = traitlets.Dict()
    current_to_irr_trait = traitlets.Dict()
    
    def __init__(self):
        # dropdown to select device (probe or test matrix)
        self.select_device = widgets.Dropdown(options=[('HearLight device', 1), ('Test matrix', 2)], layout = {'width' : '100%'})
        traitlets.link((self.select_device, 'value'), (self, 'device_trait'))
        
        # dropdown to select shield version
        self.select_shield = widgets.Dropdown(options=[('HearLight shield v1 w/ext power supply', 1), ('HearLight shield v1', 2)], layout = {'width' : '100%'})
        traitlets.link((self.select_shield, 'value'), (self, 'shield_trait'))
        
        # toggle button for simple or advanced mode
        self.adv_toggle_button = widgets.ToggleButton(description='Advanced', value=False, disabled=False)
        self.adv_toggle_button.add_class('adv_toggle_button')
        def adv_setting_transform(tf):
            return True if tf == False else False
        
        # dropdown to select overlay to program
        self.ol = None
        self.overlay_select = widgets.Dropdown(options=OVERLAYS.keys(), layout = {'width' : '100%'})
        
        # button to program bitstream
        self.program_overlay_button = widgets.Button(description='Program FPGA', icon='download')
        self.program_overlay_button.on_click(self.program_overlay)
        
        # dropdown for maximum LED current
        self.led_max_current_select = widgets.Dropdown(options=[30, 100], value=30, disabled=True, layout = {'width' : '100%'})
        traitlets.link((self.led_max_current_select, 'value'), (self, 'led_max_current_trait'))
        traitlets.dlink((self.adv_toggle_button, 'value'), (self.led_max_current_select, 'disabled'), adv_setting_transform)
        
        # entry boxes for maximum channel, switch and device currents 
        self.channel_max_current_select = widgets.FloatText(value=300, disabled=True, layout = {'width' : '100%'})
        traitlets.link((self.channel_max_current_select, 'value'), (self, 'channel_max_current_trait'))
        traitlets.dlink((self.adv_toggle_button, 'value'), (self.channel_max_current_select, 'disabled'), adv_setting_transform)
        
        self.switch_max_current_select = widgets.FloatText(value=130, disabled=True, layout = {'width' : '100%'})
        traitlets.link((self.switch_max_current_select, 'value'), (self, 'switch_max_current_trait'))
        traitlets.dlink((self.adv_toggle_button, 'value'), (self.switch_max_current_select, 'disabled'), adv_setting_transform)
       
        self.device_max_current_select = widgets.FloatText(value=2500, disabled=True, layout = {'width' : '100%'})
        traitlets.link((self.device_max_current_select, 'value'), (self, 'device_max_current_trait'))
        traitlets.dlink((self.adv_toggle_button, 'value'), (self.device_max_current_select, 'disabled'), adv_setting_transform)
        
        # dropdown for DAC reference current
        self.dac_ref = widgets.Dropdown(options=[3.125, 6.25, 12.5, 25, 50, 100, 200, 300], value=6.25, disabled=True, layout = {'width' : '100%'})
        self.dac_ref.add_class('dac_ref')
        self.dac_ref_commands = {'3.125' : 0, '6.25' : 1, '12.5' : 2, '25.0' : 3, '50.0' : 4, '100.0' : 5, '200.0' : 6, '300.0' : 7}
        traitlets.link((self.dac_ref, 'value'), (self, 'dac_ref_trait'))
        traitlets.dlink((self.adv_toggle_button, 'value'), (self.dac_ref, 'disabled'), adv_setting_transform)
        
        # file uploads for irradiance to current regression coefficients
        self.irr_to_current_upload = widgets.FileUpload(accept='.dat', multiple=False, disabled=False, layout = {'width' : '130px'})
        traitlets.link((self.irr_to_current_upload, 'value'), (self, 'irr_to_current_trait'))
        self.irr_to_current_upload_path = widgets.HTML(value='<i style="color:red;">No file selected!</i>')
        
        # file upload for current to irradiance regression coefficients 
        self.current_to_irr_upload = widgets.FileUpload(accept='.dat', multiple=False, disabled=False, layout = {'width' : '130px'})
        traitlets.link((self.current_to_irr_upload, 'value'), (self, 'current_to_irr_trait'))
        self.current_to_irr_upload_path = widgets.HTML(value='<i style="color:red;">No file selected!</i>')
        
        # text box for error log
        self.log = widgets.Textarea(value='', disabled=False)
        self.log.add_class('log')
        
        # button to stop program running
        self.stop_button = widgets.Button(description='STOP', icon='stop', disabled=True)
        self.stop_button.add_class('stop_button')
        self.stop_pressed = False
                
        self.layout_panel()
        
    def program_overlay(self, trait):
        self.ol = Overlay(OVERLAYS[self.overlay_select.value])
        
    def update_log(self, log_text):
        self.log.value += log_text
        
    def layout_panel(self):
        ### main control panel box
        self.main_control_panel = widgets.Box()
        self.main_control_panel.add_class('main_control_panel_box')
        self.main_control_panel.children += (widgets.HTML(value=css), )
        
        ## setup box
        setup_box = widgets.Box()
        setup_box.add_class('setup_box')
        self.main_control_panel.children += (setup_box,)
        
        # basic setup box
        basic_setup_box = widgets.Box()
        basic_setup_box.add_class('basic_setup_box')
        basic_setup_box_heading = widgets.HTML(value='<b>&nbsp;System Setup</b>')
        basic_setup_box_heading.add_class('section_heading')
        advanced_toggle_button_box = widgets.Box()
        advanced_toggle_button_box.add_class('advanced_toggle_button_box')
        advanced_toggle_button_box.children += (self.adv_toggle_button, )
        setup_box.children += (basic_setup_box_heading, basic_setup_box, advanced_toggle_button_box)
        
        # basic setup select device box
        basic_setup_select_device_box = widgets.Box()
        basic_setup_select_device_box.add_class('basic_setup_select_device_box')
        select_device_box = widgets.Box()
        select_device_box.add_class('label_setting_box')
        select_device_box.children += (widgets.Label('Select device: '), self.select_device, )
        select_shield_box = widgets.Box()
        select_shield_box.add_class('label_setting_box')
        select_shield_box.children += (widgets.Label('Select shield: '), self.select_shield, )
        basic_setup_select_device_box.children += (select_device_box, 
                                                   select_shield_box, )
        basic_setup_box.children += (basic_setup_select_device_box,)

        # basic setup bitstream box
        basic_setup_bitstream_box = widgets.Box()
        basic_setup_bitstream_box.add_class('basic_setup_bitstream_box')
        overlay_select_box = widgets.Box()
        overlay_select_box.add_class('label_setting_box')
        overlay_select_box.children += (widgets.Label('Choose overlay: '), self.overlay_select, )
        basic_setup_bitstream_box.children += (overlay_select_box,)
        basic_setup_box.children += (basic_setup_bitstream_box,)
        
        # basic setup bitstream button box 
        basic_setup_bitstream_button_box = widgets.Box()
        basic_setup_bitstream_button_box.add_class('basic_setup_bitstream_button_box')
        basic_setup_bitstream_button_box.children += (self.program_overlay_button, )
        basic_setup_bitstream_box.children += (basic_setup_bitstream_button_box,)        

        # advanced setup box
        advanced_setup_box = widgets.Box()
        advanced_setup_box.add_class('advanced_setup_box')
        setup_box.children += (advanced_setup_box,)
        
        # advanced setup settings box
        advanced_setup_settings_box = widgets.Box()
        advanced_setup_settings_box.add_class('advanced_setup_settings_box')
        led_max_current_select_box = widgets.Box()
        led_max_current_select_box.add_class('label_setting_box')
        led_max_current_select_box.children += (widgets.Label('Max. LED current (mA): '), self.led_max_current_select, )
        
        channel_max_current_select_box = widgets.Box()
        channel_max_current_select_box.add_class('label_setting_box')
        channel_max_current_select_box.children += (widgets.Label('Max. channel current (mA): '), self.channel_max_current_select, )
        
        switch_max_current_select_box = widgets.Box()
        switch_max_current_select_box.add_class('label_setting_box')
        switch_max_current_select_box.children += (widgets.Label('Max. switch current (mA): '), self.switch_max_current_select, )
        
        device_max_current_select_box = widgets.Box()
        device_max_current_select_box.add_class('label_setting_box')
        device_max_current_select_box.children += (widgets.Label('Max. device current (mA): '), self.device_max_current_select, )

        dac_ref_box = widgets.Box()
        dac_ref_box.add_class('label_setting_box')
        dac_ref_box.children += (widgets.Label('DAC reference (mA): '), self.dac_ref, )
        
        advanced_setup_settings_box.children += (#self.adv_toggle_button,
                                                 led_max_current_select_box, 
                                                 channel_max_current_select_box, 
                                                 switch_max_current_select_box, 
                                                 device_max_current_select_box, 
                                                 dac_ref_box, )
        advanced_setup_box.children += (advanced_setup_settings_box,)
        
        # advanced setup files box
        advanced_setup_files_box = widgets.Box()
        advanced_setup_files_box.add_class('advanced_setup_files_box')
        advanced_setup_box.children += (advanced_setup_files_box,)
        
        # advanced setup irr to current box
        advanced_setup_irr_to_current_box = widgets.Box()
        advanced_setup_irr_to_current_box.add_class('label_setting_box')
        advanced_setup_irr_to_current_box.children += (widgets.Label('Irradiance to current file: '), self.irr_to_current_upload, )
        advanced_setup_irr_to_current_box.children += (self.irr_to_current_upload_path, )
        advanced_setup_files_box.children += (advanced_setup_irr_to_current_box, )

        # advanced setup current to irr box
        advanced_setup_current_to_irr_box = widgets.Box()
        advanced_setup_current_to_irr_box.add_class('label_setting_box')
        advanced_setup_current_to_irr_box.children += (widgets.Label('Current to irradiance file: '), self.current_to_irr_upload, )
        advanced_setup_current_to_irr_box.children += (self.current_to_irr_upload_path, )
        advanced_setup_files_box.children += (advanced_setup_current_to_irr_box, )
        
        ## interact box
        interact_box = widgets.Box()
        interact_box.add_class('interact_box')
        self.main_control_panel.children += (interact_box,)
        
        # interact box heading
        interact_box_heading = widgets.HTML(value='<b>&nbsp;Log</b>')
        interact_box_heading.add_class('section_heading')
        interact_box.children += (interact_box_heading,)
        
        # interact log box
        interact_log_box = widgets.Box()
        interact_log_box.add_class('interact_log_box')
        interact_log_box.children += (self.log, )
        interact_box.children += (interact_log_box,)
        
        # interact control box heading
        interact_box_heading = widgets.HTML(value='<b>&nbsp;System Control</b>')
        interact_box_heading.add_class('section_heading')
        interact_box.children += (interact_box_heading,)
        
        # interact start/stop button box
        interact_start_stop_box = widgets.Box()
        interact_start_stop_box.add_class('interact_start_stop_box')
        interact_start_stop_box.children += (self.stop_button, )
        interact_box.children += (interact_start_stop_box,)

"""Class for the LEDs selector.

"""
class SelectLEDs():
    def __init__(self, control_array):
        self.control_array = control_array
                
        self.leds_clicked = [[False] * N_CHANNELS for _ in range(N_SWITCHES)]

        self.led_grid = widgets.Box()
        
        # display button to load LED grid
        self.load_grid_button = widgets.Button(description='load grid')
        self.load_grid_button.on_click(self.load_grid_button_clicked)
        self.led_grid.add_class('led_grid_loading')
        self.led_grid.children = [self.load_grid_button]
        
    def load_grid_button_clicked(self, load_grid_button):
        # display loading bar widget
        self.loading = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description='Loading:',
            bar_style='info', # 'success', 'info', 'warning', 'danger' or ''
            style={'bar_color': '#635faa'},
            orientation='horizontal'
        )
        self.led_grid.add_class('led_grid_loading')
        self.led_grid.children = [self.loading]
        
        asyncio.ensure_future(self.get_led_grid())
        
    async def get_led_grid(self):
        led_grid_temp = widgets.Box()
        led_grid_temp.add_class('led_grid')
                
        for row in range(N_SWITCHES):
            for col in range(N_CHANNELS):
                #print('test')
                
                led_indicator = widgets.Button()
                led_indicator.add_class('led_indicator')
                led_indicator.on_click(self.led_clicked)
                setattr(led_indicator, 'led_row_idx', row)
                setattr(led_indicator, 'led_col_idx', col)
                
                button_box = widgets.Box()
                button_box.layout = {'width' : '40px', 'height' : '40px', 'grid-area' : f'{row}{col}'}
                button_box.children += (led_indicator,)
                
                led_grid_temp.children += (button_box,)
                
                self.loading.value += 1
                #await asyncio.sleep(0.01)
            await asyncio.sleep(1)
        
        self.led_grid.remove_class('led_grid_loading')
        self.led_grid.add_class('led_grid')                
        self.led_grid.children = led_grid_temp.children
        
    def clear_button_clicked(self, btn):
        for row in range(N_SWITCHES):
            for col in range(N_CHANNELS):
                self.leds_clicked[row][col] = False
                self.led_grid.children[row*10+col].children[0].remove_class('led_indicator_clicked')
                
        # update switch states and channel states
        self.control_array.get_switch_states()
        self.control_array.get_channel_states()
            
        # update LED indicator
        self.control_array.indicate_leds.update_led_indicator(self.control_array.channel_states, self.control_array.switch_states)
        
        # update channel currents
        self.control_array.get_channel_currents([])                
        
        
    def led_clicked(self, led_indicator):
        if self.leds_clicked[led_indicator.led_row_idx][led_indicator.led_col_idx] == False:
            led_indicator.add_class('led_indicator_clicked')
            self.leds_clicked[led_indicator.led_row_idx][led_indicator.led_col_idx] = True
        else:
            led_indicator.remove_class('led_indicator_clicked')
            self.leds_clicked[led_indicator.led_row_idx][led_indicator.led_col_idx] = False

        # update switch states and channel states
        self.control_array.get_switch_states()
        self.control_array.get_channel_states()
            
        # update LED indicator
        self.control_array.indicate_leds.update_led_indicator(self.control_array.channel_states, self.control_array.switch_states)
        
        # update channel currents
        self.control_array.get_channel_currents([])
        
"""Class for the LEDs indicator.

"""
class IndicateLEDs():
    def __init__(self):        
        self.matrix_output = np.array([[False] * N_CHANNELS for _ in range(N_SWITCHES)])

        self.led_grid = widgets.Box()

        # display button to load LED grid
        self.load_grid_button = widgets.Button(description='load grid')
        self.load_grid_button.on_click(self.load_grid_button_clicked)
        self.led_grid.add_class('led_grid_loading')
        self.led_grid.children = [self.load_grid_button]
        
    def load_grid_button_clicked(self, load_grid_button):
        # display loading bar widget
        self.loading = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description='Loading:',
            bar_style='info', # 'success', 'info', 'warning', 'danger' or ''
            style={'bar_color': '#635faa'},
            orientation='horizontal'
        )
        self.led_grid.add_class('led_grid_loading')
        self.led_grid.children = [self.loading]
        
        asyncio.ensure_future(self.get_led_grid())

    async def get_led_grid(self):
        led_grid_temp = widgets.Box()
        led_grid_temp.add_class('led_grid')
                
        for row in range(N_SWITCHES):
            for col in range(N_CHANNELS):                
                led_indicator = widgets.Box()
                led_indicator.add_class('led_indicator')
                setattr(led_indicator, 'led_row_idx', row)
                setattr(led_indicator, 'led_col_idx', col)
                
                led_box = widgets.Box()
                led_box.layout = {'width' : '40px', 'height' : '40px', 'grid-area' : f'{row}{col}'}
                led_box.children += (led_indicator,)
                
                led_grid_temp.children += (led_box,)
                
                self.loading.value += 1
            await asyncio.sleep(1)
        
        self.led_grid.remove_class('led_grid_loading')
        self.led_grid.add_class('led_grid')
        self.led_grid.children = led_grid_temp.children
        
    def led_off(self, row, col):
        self.led_grid.children[row * N_SWITCHES + col].children[0].remove_class('led_indicator_clicked')
        
    def led_on(self, row, col):
        self.led_grid.children[row * N_SWITCHES + col].children[0].add_class('led_indicator_clicked')
        
    def update_led_indicator(self, channel_states, switch_states):
        self.matrix_output = np.matmul(np.transpose(switch_states), channel_states)
        
        for row in range(N_SWITCHES):
            if switch_states[0][row] == False:
                for c in range(N_CHANNELS):
                    self.led_off(row, c)
                continue
            for col in range(N_CHANNELS):
                if channel_states[0][col] == False:
                    self.led_off(row, col)
                else:
                    self.led_on(row, col)

"""Class for the LEDs control panel.

"""
class LEDControlPanel(traitlets.HasTraits):
    peak_irr_trait = traitlets.Float()
    
    def __init__(self, control_array):
        # led grid to select LEDs
        # start background task to allow user to work while grid is loading
        #self.select_led_grid_gen_task = asyncio.ensure_future(control_array.select_leds.get_led_grid())
        self.select_led_grid = control_array.select_leds.led_grid
        
        # button to clear selected LEDs
        self.clear_leds_button = widgets.Button(description='CLEAR', icon='restart')
        self.clear_leds_button.add_class('clear_leds_button')
        self.clear_leds_button.on_click(control_array.select_leds.clear_button_clicked)
        
        # led grid to indicate actual LEDs
        #self.indicate_led_grid_gen_task = asyncio.ensure_future(control_array.indicate_leds.get_led_grid())
        self.indicate_led_grid = control_array.indicate_leds.led_grid

        # box to indicate trigger signal
        self.trigger_signal_box = widgets.Box()
        self.trigger_signal_box.add_class('trigger_signal_box')
        
        # float text for peak irradiance (mW/mm^2)
        self.peak_irr_select = widgets.FloatText(min=0, max=100, value=20)
        self.peak_irr_select.add_class('peak_irr_select')
        traitlets.link((self.peak_irr_select, 'value'), (self, 'peak_irr_trait'))

        # float text for pulse duration (ms)
        self.pulse_duration_select = widgets.FloatText(min=0, value=500)
        self.pulse_duration_select.add_class('pulse_duration_select')
        
        # float text for pulse frequency (Hz)
        self.pulse_frequency_select = widgets.FloatText(min=0, value=1)
        self.pulse_frequency_select.add_class('pulse_frequency_select')
        
        # int text for number of pulses
        self.no_pulses_select = widgets.IntText(min=0, value=3)
        self.no_pulses_select.add_class('no_pulses_select')
        
        # button to start protocol
        self.start_button = widgets.Button(description='START', icon='play')
        self.start_button.add_class('start_button')
       
        # file upload for complex pattern configuration file
        self.complex_pattern_file_upload = widgets.FileUpload(accept='.txt', multiple=False)
        self.complex_pattern_file_upload_path = widgets.HTML(value='<i style="color:#229abc;">No file selected!</i>')
        
        # text entry to display and allow editing of complex pattern
        self.complex_pattern_text = widgets.Textarea()
        self.complex_pattern_text.add_class('complex_pattern_text')
        
        self.layout_panel()
        
    def layout_panel(self):
        self.led_control_panel = widgets.Box()
        self.led_control_panel.add_class('led_control_panel')
        self.led_control_panel.children += (widgets.HTML(value=css), )
        
        control_leds_panel = widgets.Box()
        control_leds_panel.add_class('control_leds_panel')
        self.led_control_panel.children += (control_leds_panel, )
        
        control_leds_panel_heading = widgets.HTML(value='<b>&nbsp;Requested LEDs</b>')
        control_leds_panel_heading.add_class('section_heading')
        control_leds_panel.children += (control_leds_panel_heading, )        
        
        control_leds_box = widgets.Box()
        control_leds_box.add_class('control_leds_box')
        control_leds_box.children += (self.select_led_grid, )
        control_leds_panel.children += (control_leds_box, )
        
        clear_leds_button_box = widgets.Box()
        clear_leds_button_box.add_class('clear_leds_button_box')
        clear_leds_button_box.children += (self.clear_leds_button, )
        control_leds_panel.children += (clear_leds_button_box, )
        
        indicate_leds_panel = widgets.Box()
        indicate_leds_panel.add_class('indicate_leds_panel')
        self.led_control_panel.children += (indicate_leds_panel, )

        indicate_leds_panel_heading = widgets.HTML(value='<b>&nbsp;Actual LEDs Illuminated</b>')
        indicate_leds_panel_heading.add_class('section_heading')
        indicate_leds_panel.children += (indicate_leds_panel_heading, )  
        
        indicate_leds_box = widgets.Box()
        indicate_leds_box.add_class('indicate_leds_box')
        indicate_leds_box.children += (self.indicate_led_grid, )
        indicate_leds_panel.children += (indicate_leds_box, )
        
        trigger_indicator_box = widgets.Box()
        trigger_indicator_box.add_class('trigger_indicator_box')
        trigger_indicator_box.children += (widgets.HTML('<b>TRIGGER</b>'), self.trigger_signal_box, )
        indicate_leds_panel.children += (trigger_indicator_box, )        
        
        led_parameters_panel = widgets.Box()
        led_parameters_panel.add_class('led_parameters_panel')
        self.led_control_panel.children += (led_parameters_panel, )
        
        config_panel_heading = widgets.HTML(value='<b>&nbsp;Configure Pattern</b>')
        config_panel_heading.add_class('section_heading')
        led_parameters_panel.children += (config_panel_heading, )
        
        config_tab = widgets.Tab()
        config_tab.add_class('config_tab')
        led_parameters_panel.children += (config_tab, )
        
        simple_config_box = widgets.Box()
        simple_config_box.add_class('simple_config_box')
        
        peak_irr_select_box = widgets.Box()
        peak_irr_select_box.add_class('config_setting_box')
        peak_irr_select_box.children += (widgets.Label('Peak irradiance (mW/mm^2): '), self.peak_irr_select, )
        simple_config_box.children += (peak_irr_select_box, )

        pulse_duration_select_box = widgets.Box()
        pulse_duration_select_box.add_class('config_setting_box')
        pulse_duration_select_box.children += (widgets.Label('Pulse duration (ms): '), self.pulse_duration_select, )
        simple_config_box.children += (pulse_duration_select_box, )
        
        pulse_frequency_select_box = widgets.Box()
        pulse_frequency_select_box.add_class('config_setting_box')
        pulse_frequency_select_box.children += (widgets.Label('Pulse frequency (Hz): '), self.pulse_frequency_select, )
        simple_config_box.children += (pulse_frequency_select_box, )
        
        no_pulses_select_box = widgets.Box()
        no_pulses_select_box.add_class('config_setting_box')
        no_pulses_select_box.children += (widgets.Label('Number of pulses: '), self.no_pulses_select, )
        simple_config_box.children += (no_pulses_select_box, )
        
        simple_config_box.children += (self.start_button, )
        
        complex_config_box = widgets.Box()
        complex_config_box.add_class('complex_config_box')
        
        config_file_upload_box = widgets.Box()
        config_file_upload_box.add_class('config_file_upload_box')
        config_file_upload_box.children += (widgets.Label('Select config file (.txt): '), self.complex_pattern_file_upload,)
        complex_config_box.children += (config_file_upload_box,)
        complex_config_box.children += (self.complex_pattern_file_upload_path, )
        
        config_text_box = widgets.Box()
        config_text_box.add_class('config_text_box')
        config_text_box.children += (self.complex_pattern_text,)
        complex_config_box.children += (config_text_box,)
        
        config_tab.children += (simple_config_box, )
        config_tab.set_title(0, 'Single pattern')
        config_tab.children += (complex_config_box, )
        config_tab.set_title(1, 'Complex pattern')
        
"""Class for panel which shows required LED currents/channel currents and actual LED irradiances in tables.

"""
class ArrayCurrentsPanel():
    def __init__(self):
        # table to display required currents for given irradiance and selection of LEDs
        self.required_currents_label = widgets.HTML(value='<b>&nbsp;LED currents (mA) required</b>')
        self.required_currents_label.add_class('section_heading')
        self.required_currents_table = widgets.HBox()
        self.required_currents_table.add_class('required_currents_table')
        self.required_currents_table.children = [widgets.VBox(children=[widgets.Box(children=[widgets.HTML(value='0')], layout={'height' : f'calc({REQUIRED_CURRENTS_HEIGHT}/10)', 'width' : f'calc({REQUIRED_CURRENTS_WIDTH}-2px)/10)', 'border' : 'solid 1px black', 'margin' : 'none'}) for _ in range(N_SWITCHES)], 
                                                  layout={'height' : f'calc({REQUIRED_CURRENTS_HEIGHT}-2px)', 'width' : f'calc({REQUIRED_CURRENTS_WIDTH}/10)', 'border' : 'none', 'margin' : 'none'}) for _ in range(N_CHANNELS)]
        self.required_currents_panel = widgets.VBox(children=[self.required_currents_label, self.required_currents_table])

        # table to display actual channel currents based on required LED currents based on maximum parameters
        self.channel_currents_label = widgets.HTML(value='<b>&nbsp;Actual channel currents (mA)</b>')
        self.channel_currents_label.add_class('section_heading')      
        self.channel_currents_table = widgets.HBox()
        self.channel_currents_table.add_class('channel_currents_table')
        self.channel_currents_table.children = [widgets.Box(children=[widgets.HTML(value='0')], layout={'height' : f'calc({CHANNEL_CURRENTS_HEIGHT}-2px)', 'width' : f'calc({CHANNEL_CURRENTS_WIDTH}/10)', 'border' : 'solid 1px black', 'margin' : 'none'}) for _ in range(N_CHANNELS)]
        self.channel_currents_panel = widgets.VBox(children=[self.channel_currents_label, self.channel_currents_table])
        
        # table to display actual LED irradiances based on actual channel currents and closed switches
        self.actual_irradiances_label = widgets.HTML(value='<b>&nbsp;Actual LED irradiances (mW/mm^2)</b>')
        self.actual_irradiances_label.add_class('section_heading')
        self.actual_irradiances_table = widgets.HBox()
        self.actual_irradiances_table.add_class('actual_irradiances_table')
        self.actual_irradiances_table.children = [widgets.VBox(children=[widgets.Box(children=[widgets.HTML(value='0')], layout={'height' : f'calc({ACTUAL_IRRADIANCES_HEIGHT}/10)', 'width' : f'calc({ACTUAL_IRRADIANCES_WIDTH}-2px)/10)', 'border' : 'solid 1px black', 'margin' : 'none'}) for _ in range(N_SWITCHES)], 
                                                  layout={'height' : f'calc({ACTUAL_IRRADIANCES_HEIGHT}-2px)', 'width' : f'calc({ACTUAL_IRRADIANCES_WIDTH}/10)', 'border' : 'none', 'margin' : 'none'}) for _ in range(N_CHANNELS)]
        self.actual_irradiances_panel = widgets.VBox(children=[self.actual_irradiances_label, self.actual_irradiances_table])
        
    def edit_required_currents_value(self, row, col, value):
        self.required_currents_table.children[col].children[row].children[0].value = '{:.3f}'.format(value)
        
    def edit_channel_currents_value(self, col, value):
        self.channel_currents_table.children[col].children[0].value = '{:.3f}'.format(value)
        
    def edit_actual_irradiances_value(self, row, col, value):
        self.actual_irradiances_table.children[col].children[row].children[0].value = '{:.3f}'.format(value)
    
"""Main class for accessing dashboard panels for the HearLight system.

"""
class Dashboard():
    def __init__(self, led_control_panel = False, array_currents_panel = False, audio_control_panel = None):
        self.led_control_panel_active = led_control_panel
        self.array_currents_panel_active = array_currents_panel
        
        ## banner panel
        self.banner_panel_inst = BannerPanel()
        self.banner_panel = self.banner_panel_inst.banner_image_box
        
        ## info panel
        self.info_panel_inst = InfoPanel()
        self.info_panel = self.info_panel_inst.info_panel
        
        ## main control panel
        self.main_control_panel_inst = MainControlPanel()
        self.main_control_panel_inst.observe(self.get_coeffs_matrix_L_to_I, names=['irr_to_current_trait'])
        self.main_control_panel_inst.observe(self.get_coeffs_matrix_I_to_L, names=['current_to_irr_trait'])
        if(self.led_control_panel_active):
            self.main_control_panel_inst.observe(self.get_channel_currents, names=['led_max_current_trait', 'channel_max_current_trait', 'switch_max_current_trait', 'device_max_current_trait', 'dac_ref_trait'])
            self.main_control_panel_inst.observe(self.led_control_config, names=['dac_ref_trait'])

        self.main_control_panel = self.main_control_panel_inst.main_control_panel

        ## led control panel
        if(self.led_control_panel_active):
            self.select_leds = SelectLEDs(self)
            self.indicate_leds = IndicateLEDs()
            self.led_control_panel_inst = LEDControlPanel(self)
            self.led_control_panel_inst.observe(self.get_channel_currents, names=['peak_irr_trait'])
        
            self.led_control_panel = self.led_control_panel_inst.led_control_panel
            
            self.led_control_panel_inst.start_button.on_click(self.run_basic_control)

        ## array currents panel
        if(self.array_currents_panel_active):
            self.array_currents_panel_inst = ArrayCurrentsPanel()
            self.required_currents_panel = self.array_currents_panel_inst.required_currents_panel
            self.channel_currents_panel = self.array_currents_panel_inst.channel_currents_panel
            self.actual_irradiances_panel = self.array_currents_panel_inst.actual_irradiances_panel
        
        ## parameters relating to state of system - only valid when LED control panel is being used
        if(self.led_control_panel_active):
            self.channel_states = np.array([False] * N_CHANNELS, ndmin=2)  # channel off is false
            self.switch_states = np.array([False] * N_SWITCHES, ndmin=2) # switches open is false

            self.channel_currents = np.array([0] * N_CHANNELS) # measured in mA

            self.channel_counts = np.array([0] * N_CHANNELS) # measured in DAC counts (0 -> 65535)

        self.coeffs_matrix_L_to_I = None
        self.coeffs_matrix_I_to_L = None

        self.basic_driver = None
        
        self.ol = None
        
        ## audio control panel
        if audio_control_panel != None:
            self.audio_control_panel_inst = AudioControlPanel(audio_control_panel)
            self.audio_control_panel = self.audio_control_panel_inst.audio_control_panel
            
            # link traits in 'audio processor' class (e.g. AudioSoftwareProcessorFFT - 'audio_control_panel' parameter to class init) to traits in main control panel
            traitlets.link((self.main_control_panel_inst, 'led_max_current_trait'), (self.audio_control_panel_inst.processor, 'led_max_current_trait'))
            traitlets.link((self.main_control_panel_inst, 'channel_max_current_trait'), (self.audio_control_panel_inst.processor, 'channel_max_current_trait'))
            traitlets.link((self.main_control_panel_inst, 'switch_max_current_trait'), (self.audio_control_panel_inst.processor, 'switch_max_current_trait'))
            traitlets.link((self.main_control_panel_inst, 'device_max_current_trait'), (self.audio_control_panel_inst.processor, 'device_max_current_trait'))
            traitlets.link((self.main_control_panel_inst, 'dac_ref_trait'), (self.audio_control_panel_inst.processor, 'dac_ref_trait'))
            traitlets.link((self.main_control_panel_inst, 'irr_to_current_trait'), (self.audio_control_panel_inst.processor, 'irr_to_current_trait'))
            traitlets.link((self.main_control_panel_inst, 'current_to_irr_trait'), (self.audio_control_panel_inst.processor, 'current_to_irr_trait'))
            
            self.audio_control_panel_inst.processor.update_main_control_panel_log = self.main_control_panel_inst.update_log
            
            # the audio processing takes priority so cannot program overlay for basic LED control
            self.main_control_panel_inst.program_overlay_button.disabled = True
            
    def get_switch_states(self):
        """Gets array of required switch positions
        Called when the pattern is updated
        """
        switch_states = np.array([False] * N_SWITCHES)
        for select_led_col in np.transpose(np.array(self.select_leds.leds_clicked)):
            switch_states = switch_states | select_led_col
        self.switch_states[0] = switch_states
        
    def get_channel_states(self):
        """Gets array of channels which will be active
        Called when pattern is updated
        """
        channel_states = np.array([False] * N_CHANNELS)
        for select_led_row in np.array(self.select_leds.leds_clicked):
            channel_states = channel_states | select_led_row
        self.channel_states[0] = channel_states
        
    def get_coeffs_matrix_L_to_I(self, change):
        """Called when the file select for regression coefficients is changed.
        """
        # irradiance to current...
        # open file and read irradiance to current regression coefficients
        data_str = self.main_control_panel_inst.irr_to_current_upload.data[0].decode("utf-8").split('\n')[0:-1]

        # get regression coefficients as 2D numpy array
        polynomial_order = len(data_str[0].split(',')) - 1
        self.coeffs_matrix_L_to_I = np.reshape(np.asarray([d.split(',') for d in data_str]).astype(float), (10,10,polynomial_order+1))

        self.main_control_panel_inst.irr_to_current_upload_path.value = f"<i style='color:green;'>{self.main_control_panel_inst.irr_to_current_upload.metadata[0]['name']}</i>"
        
        self.get_channel_currents(0)
        
    def get_coeffs_matrix_I_to_L(self, change):
        """Called when the file select for regression coefficients is changed.
        """
        # current to irradiance...
        data_str = self.main_control_panel_inst.current_to_irr_upload.data[0].decode("utf-8").split('\n')[0:-1]

        polynomial_order = len(data_str[0].split(',')) - 1
        self.coeffs_matrix_I_to_L = np.reshape(np.asarray([d.split(',') for d in data_str]).astype(float), (10,10,polynomial_order+1))

        self.main_control_panel_inst.current_to_irr_upload_path.value = f"<i style='color:green;'>{self.main_control_panel_inst.current_to_irr_upload.metadata[0]['name']}</i>"
        
        self.get_channel_currents(0)
        
    def get_channel_currents(self, trait):
        """Gets the channel currents for chosen LED pattern, peak irradiance and coefficients
        Called when the pattern, peak irradiance or any setting from 'main control panel' gets updated including file opens
        """     
        peak_irr = self.led_control_panel_inst.peak_irr_trait
        led_max_current = self.main_control_panel_inst.led_max_current_trait
        channel_max_current = self.main_control_panel_inst.channel_max_current_trait
        switch_max_current = self.main_control_panel_inst.switch_max_current_trait
        device_max_current = self.main_control_panel_inst.device_max_current_trait
        dac_ref = self.main_control_panel_inst.dac_ref_trait
        
        if (self.coeffs_matrix_L_to_I is None) or (self.coeffs_matrix_I_to_L is None):
            self.main_control_panel_inst.update_log('ERROR: Load coefficients!\n')
            return
        
        error_log_text = f""
        
        if peak_irr == 0 or np.array_equal(self.indicate_leds.matrix_output, np.zeros(shape=(N_SWITCHES, N_CHANNELS))):
            required_currents = np.zeros(shape=(N_SWITCHES, N_CHANNELS), dtype=float)
            channel_currents = np.zeros(shape=(1,N_CHANNELS), dtype=float)
            actual_led_irradiances = np.zeros(shape=(N_SWITCHES, N_CHANNELS), dtype=float)
            
        else:
            # get matrix of required currents
            irr_matrix = np.array([[peak_irr] * N_CHANNELS for _ in range(N_SWITCHES)])
            required_currents = np.asarray([[np.poly1d(coeffs)(peak_irr) for coeffs in self.coeffs_matrix_L_to_I[r]] for r in range(N_SWITCHES)]) * self.indicate_leds.matrix_output

            # check for any erraneous negative currents caused by fitting regression on a bad LED - set to zero
            required_currents[required_currents < 0] = 0
            
            # check if individual LED maximum current is being exceeded and set to maximum if so
            required_currents[required_currents > led_max_current] = led_max_current
            
            # warn user if required current is zero for an LED that should be on (i.e. a short on the same column)
            for channel, channel_idx in zip(np.transpose(required_currents), range(10)):
                if any(self.switch_states[0] & np.array(channel == 0)) and any(channel > 0):
                    # !!! this line is potentially dangerous - allows current to flow through parallel short - may overheat/damage device or damage switch array ICs
                    # channel[self.switch_states[0] & np.array(channel == 0)] = np.amin(channel[channel > 0])
                    error_log_text += f"WARNING: channel P{10 - channel_idx} current set to zero to avoid passing current through a short\n"

            n_switches_closed = self.switch_states[0].sum()

            # get required channel currents from matrix of required currents unless required currents all zero
            channel_currents = np.zeros(shape=(1,N_CHANNELS), dtype=float)
            if not np.array_equal(required_currents, np.zeros(shape=(N_SWITCHES, N_CHANNELS))):
                channel_currents[0][self.channel_states[0]] = np.amin(required_currents[self.switch_states[0],:][:,self.channel_states[0]], axis=0) * n_switches_closed
                
            # check if channel current exceeded for any channel
            if any(channel_currents[0] > channel_max_current):
                error_log_text += f"WARNING: channel current limit reached on {str(np.array(['P'+str(r) for r in range(1,11,1)])[channel_currents[0][::-1] > channel_max_current])[1:-1]}\n- currents have been automatically adjusted to maximum available\n"
                channel_currents[0][channel_currents[0] > channel_max_current] = channel_max_current            

            # check if any switch current exceeded
            requested_switch_current = np.sum(channel_currents[0]) / n_switches_closed
            if requested_switch_current > switch_max_current:
                channel_currents[0] = channel_currents[0] / requested_switch_current * switch_max_current
                error_log_text += f"WARNING: switch current limit reached on {str(np.array(['N'+str(r) for r in range(1,11,1)])[self.switch_states[0][::-1]])[1:-1]}\n- currents have been automatically adjusted to maximum\n"

            # check if maximum device current exceeded
            requested_device_current = np.sum(channel_currents[0])
            if requested_device_current > device_max_current:
                channel_currents[0] = channel_currents[0] / requested_device_current * device_max_current
                error_log_text += f"WARNING: device current limit reached\n- currents have been automatically adjusted to maximum available"

            # check if DAC ref exceeded
            if any(channel_currents[0] > dac_ref):
                channel_currents[channel_currents > dac_ref] = dac_ref
                error_log_text += f"WARNING: DAC current reference limit reached\n- currents have been automatically adjusted to maximum\n"
            
            actual_led_irradiances = np.asarray([[np.poly1d(self.coeffs_matrix_I_to_L[r][c])(channel_currents[0][c]/n_switches_closed) for c in range(N_CHANNELS)] for r in range(N_SWITCHES)]) * self.indicate_leds.matrix_output
            
        # update error log
        self.main_control_panel_inst.update_log(error_log_text)
            
        # update information tables
        if(self.array_currents_panel_active):
            for col in range(N_CHANNELS):
                self.array_currents_panel_inst.edit_channel_currents_value(col, channel_currents[0][col])
                for row in range(N_SWITCHES):
                    self.array_currents_panel_inst.edit_required_currents_value(row, col, required_currents[row][col])
                    self.array_currents_panel_inst.edit_actual_irradiances_value(row, col, actual_led_irradiances[row][col])
            
        self.required_currents = required_currents
        self.channel_currents = channel_currents
        self.channel_counts = ((self.channel_currents / dac_ref * (2**16-1)) * self.channel_states[0].astype(int)).astype(int)
        
    def led_control_config(self, change):
        """Call when overlay is loaded or dac ref is changed
        """
        self.ol = self.main_control_panel_inst.ol
        if self.ol == None:
            self.main_control_panel_inst.update_log('ERROR: Program overlay!\n')
            return
        
        self.basic_driver = ControlLEDs(self.ol)
        
        # ALL SWITCHES OPEN
        for i in range(10):
            self.basic_driver.switch_control(i, 0)
    
        # SWITCH OFF ALL DAC CHANNELS
        for i in range(10):
            self.basic_driver.dac_channel_control(i, 0, 0)
            
        dac_ref = self.main_control_panel_inst.dac_ref_commands[str(self.main_control_panel_inst.dac_ref_trait)]
            
        # SET SOFTSPAN RANGE FOR ALL DACS
        for i in range(10):
            self.basic_driver.dac_config(i, dac_ref)
                
    def run_basic_control(self, btn):
        """When user presses 'start' button for basic control (selecting LEDs manually)
        """
        if self.basic_driver == None:
            self.led_control_config(0)
        
        pulse_duration_secs = self.led_control_panel_inst.pulse_duration_select.value / 1000
        pulse_time_secs = 1 / self.led_control_panel_inst.pulse_frequency_select.value
        no_pulses = self.led_control_panel_inst.no_pulses_select.value
        
        for pulse in range(no_pulses):
            if self.main_control_panel_inst.stop_pressed:
                break
            
            # LEDs on ############
            for sw in range(10):
                self.basic_driver.switch_control(sw, self.switch_states[0][sw])
            for ch in range(10):
                self.basic_driver.dac_channel_control(9-ch, 1, int(self.channel_counts[0][ch]))
            self.led_control_panel_inst.trigger_signal_box.add_class('trigger_signal_box_on')
            sleep(pulse_duration_secs)
            
            # LEDs off ############
            for ch in range(10):
                self.basic_driver.dac_channel_control(ch, 0, 0)
            for sw in range(10):
                self.basic_driver.switch_control(sw, 0)
            self.led_control_panel_inst.trigger_signal_box.remove_class('trigger_signal_box_on')
            sleep(max(0, pulse_time_secs - pulse_duration_secs))
        
    def run_protocol(self, btn):
        """When user presses 'start' button for protocol control (from file)
        """
        pass
        