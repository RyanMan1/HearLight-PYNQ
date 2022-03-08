import ipywidgets as widgets
import numpy as np
import functools
import asyncio

from .css import css

import copy

N_SWITCHES = 10
N_CHANNELS = 10

"""Class for the main control/setup panel.

"""
class MainControlPanel():
    def __init__(self):
        # dropdown to select device (probe or test matrix)
        self.select_device = widgets.Dropdown(options=['Test matrix', 'Probe 1'], layout = {'width' : '100%'})
        
        # dropdown to select shield version
        self.select_shield = widgets.Dropdown(options=['HearLight shield v1'], layout = {'width' : '100%'})
        
        # toggle button for simple or advanced mode
        self.adv_toggle_button = widgets.ToggleButton(description='Advanced', value=False, disabled=True)
        self.adv_toggle_button.add_class('adv_toggle_button')
        
        # dropdown to select overlay to program
        self.overlay_select = widgets.Dropdown(options=['Base overlay'], layout = {'width' : '100%'})
        
        # button to program bitstream
        self.program_overlay_button = widgets.Button(description='Program FPGA', icon='download')
        
        # dropdown for maximum LED current
        self.led_max_current_select = widgets.Dropdown(options=[30, 100], value=30, disabled=True, layout = {'width' : '100%'})
        
        # entry boxes for maximum channel, switch and device currents 
        self.channel_max_current_select = widgets.FloatText(value=100, disabled=True, layout = {'width' : '100%'})
        
        self.switch_max_current_select = widgets.FloatText(value=130, disabled=True, layout = {'width' : '100%'})
        
        self.device_max_current_select = widgets.FloatText(value=400, disabled=True, layout = {'width' : '100%'})
        
        # dropdown for DAC reference current
        self.dac_ref = widgets.Dropdown(options=[3.125, 6.25, 12.5, 25, 50, 100], value=100, disabled=True, layout = {'width' : '100%'})
        self.dac_ref.add_class('dac_ref')        
        self.dac_ref_commands = {'3.125' : 1, '6.25' : 2, '12.5' : 3, '25' : 4, '50' : 5, '100' : 6}
        
        # file uploads for irradiance to current regression coefficients
        self.irr_to_current_upload = widgets.FileUpload(accept='.dat', multiple=False, disabled=True)
        self.irr_to_current_upload_path = widgets.HTML(value='<i style="color:blue;">No file selected!</i>')
        
        # file upload for current to irradiance regression coefficients 
        self.current_to_irr_upload = widgets.FileUpload(accept='.dat', multiple=False, disabled=True)
        self.current_to_irr_upload_path = widgets.HTML(value='<i style="color:blue;">No file selected!</i>')
        
        # text box for error log
        self.log = widgets.Textarea(value='', disabled=False)
        self.log.add_class('log')
        
        # button to start protocol
        self.start_button = widgets.Button(description='START', icon='play')
        self.start_button.add_class('start_button')
        
        # button to stop program running
        self.stop_button = widgets.Button(description='STOP', icon='stop')
        self.stop_button.add_class('stop_button')
        
        # button for 'real-time' mode
        self.real_time_button = widgets.ToggleButton(description='Real-time mode')
        
        self.layout_panel()
        
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
        interact_start_stop_box.children += (self.start_button,
                                             self.stop_button, 
                                             self.real_time_button, )
        interact_box.children += (interact_start_stop_box,)

"""Class for the LEDs selector.

"""
class SelectLEDs():
    def __init__(self, control_array):
        self.control_array = control_array
                
        self.leds_clicked = [[False] * N_CHANNELS for _ in range(N_SWITCHES)]

        self.led_grid = widgets.Box()

        # display loading bar widget
        self.loading = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description='Loading:',
            bar_style='info', # 'success', 'info', 'warning', 'danger' or ''
            style={'bar_color': 'maroon'},
            orientation='horizontal'
        )
        self.led_grid.add_class('led_grid_loading')
        self.led_grid.children = [self.loading]
                
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
        
    def led_clicked(self, led_indicator):
        if self.leds_clicked[led_indicator.led_row_idx][led_indicator.led_col_idx] == False:
            led_indicator.add_class('led_indicator_clicked')
            self.leds_clicked[led_indicator.led_row_idx][led_indicator.led_col_idx] = True
        else:
            led_indicator.remove_class('led_indicator_clicked')
            self.leds_clicked[led_indicator.led_row_idx][led_indicator.led_col_idx] = False
            
        self.control_array.get_channel_currents()
        self.control_array.get_switch_states()

        # update LED indicator
        self.control_array.indicate_leds.update_led_indicator(self.control_array.channel_states, self.control_array.switch_states)
        
        # update channel currents
        # TEMPORARILY UNCOMMENT
        # self.control_array.regressions.irradiance_to_current(self.control_array.indicate_leds.matrix_output)

"""Class for the LEDs indicator.

"""
class IndicateLEDs():
    def __init__(self):        
        self.matrix_output = np.array([[False] * N_CHANNELS for _ in range(N_SWITCHES)])

        self.led_grid = widgets.Box()

        # display loading bar widget
        self.loading = widgets.IntProgress(
            value=0,
            min=0,
            max=100,
            description='Loading:',
            bar_style='info', # 'success', 'info', 'warning', 'danger' or ''
            style={'bar_color': 'maroon'},
            orientation='horizontal'
        )
        self.led_grid.add_class('led_grid_loading')
        self.led_grid.children = [self.loading]

    async def get_led_grid(self):
        led_grid_temp = widgets.Box()
        led_grid_temp.add_class('led_grid')
                
        for row in range(N_SWITCHES):
            for col in range(N_CHANNELS):
                #print('test')
                
                led_indicator = widgets.Box()
                led_indicator.add_class('led_indicator')
                setattr(led_indicator, 'led_row_idx', row)
                setattr(led_indicator, 'led_col_idx', col)
                
                led_box = widgets.Box()
                led_box.layout = {'width' : '40px', 'height' : '40px', 'grid-area' : f'{row}{col}'}
                led_box.children += (led_indicator,)
                
                led_grid_temp.children += (led_box,)
                
                self.loading.value += 1
                #await asyncio.sleep(0.01)
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
        
        # MAKE THIS MORE EFFICIENT???
        #
        #
        #
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
class LEDControlPanel():
    def __init__(self, control_array):
        # led grid to select LEDs
        # start background task to allow user to work while grid is loading
        self.select_led_grid_gen_task = asyncio.ensure_future(control_array.select_leds.get_led_grid())
        self.select_led_grid = control_array.select_leds.led_grid
        
        # button to clear selected LEDs
        self.clear_leds_button = widgets.Button(description='CLEAR', icon='restart')
        self.clear_leds_button.add_class('clear_leds_button')
        
        # led grid to indicate actual LEDs
        self.indicate_led_grid_gen_task = asyncio.ensure_future(control_array.indicate_leds.get_led_grid())
        self.indicate_led_grid = control_array.indicate_leds.led_grid

        # disabled button to indicate trigger signal
        self.trigger_signal_button = widgets.Button(disabled=True)
        self.trigger_signal_button.add_class('trigger_signal_button')
        
        # float text for peak irradiance (mW/mm^2)
        self.peak_irr_select = widgets.FloatText(min=0, max=100, value=20)
        self.peak_irr_select.add_class('peak_irr_select')
        
        # float text for pulse duration (ms)
        self.pulse_duration_select = widgets.FloatText(min=0, value=500)
        self.pulse_duration_select.add_class('pulse_duration_select')
        
        # float text for pulse frequency (Hz)
        self.pulse_frequency_select = widgets.FloatText(min=0, value=1)
        self.pulse_frequency_select.add_class('pulse_frequency_select')
        
        # int text for number of pulses
        self.no_pulses_select = widgets.IntText(min=0, value=3)
        self.no_pulses_select.add_class('no_pulses_select')
       
        # file upload for complex pattern configuration file
        self.complex_pattern_file_upload = widgets.FileUpload(accept='.txt', multiple=False)
        self.complex_pattern_file_upload_path = widgets.HTML(value='<i style="color:blue;">No file selected!</i>')
        
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
        trigger_indicator_box.children += (widgets.HTML('<b>TRIGGER</b>'), self.trigger_signal_button, )
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
        pass
        
"""Class to load regressions and compute required currents/actuall irradiances.

"""        
class Regressions():
    def __init__(self, peak_irr_select):
        self.peak_irr_select = peak_irr_select
        
    def irradiance_to_current(self, matrix_output):
        pass
    
    def current_to_irradiance(self):
        pass
    
"""Main class for accessing dashboard panels for the HearLight system.

"""
class HearLight():
    def __init__(self):
        
        [task.cancel for task in asyncio.all_tasks()];
        
        self.select_leds = SelectLEDs(self)
        self.indicate_leds = IndicateLEDs()
        
        self.main_control_panel_inst = MainControlPanel()
        self.main_control_panel = self.main_control_panel_inst.main_control_panel
        # TEMPORARILY COMMENTED
        self.led_control_panel_inst = LEDControlPanel(self)
        self.led_control_panel = self.led_control_panel_inst.led_control_panel
        #self.regressions = Regressions(self.main_control_panel.peak_irr_select)
        #self.main_control_panel.peak_irr_select.observe(functools.partial(self.regressions.irradiance_to_current, self.indicate_leds.matrix_output), ['value'])
        
        self.channel_states = np.array([False] * N_CHANNELS, ndmin=2)  # channel off is false
        self.switch_states = np.array([False] * N_SWITCHES, ndmin=2) # switches open is false
        
        self.channel_currents = np.array([0] * N_CHANNELS) # measured in mA
        
        self.channel_counts = np.array([0] * N_CHANNELS) # measured in DAC counts (0 -> 65535)
        
        # TEMP ##
        self.dac_ref = widgets.Dropdown(options=[3.125, 6.25, 12.5, 25, 50, 100], value=100, disabled=True, layout = {'width' : '100%'})
    
    def get_channel_currents(self):
        channel_states = np.array([False] * N_CHANNELS)
        for select_led_row in np.array(self.select_leds.leds_clicked):
            channel_states = channel_states | select_led_row
        self.channel_states[0] = channel_states
        
        self.channel_counts = ((self.channel_currents / self.dac_ref.value * (2**16-1)) * self.channel_states[0].astype(int)).astype(int)
    
    def get_switch_states(self):
        switch_states = np.array([False] * N_SWITCHES)
        for select_led_col in np.transpose(np.array(self.select_leds.leds_clicked)):
            switch_states = switch_states | select_led_col
        self.switch_states[0] = switch_states
        