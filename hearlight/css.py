# LOGO_PANEL_HEIGHT = '330px'
# LOGO_PANEL_WIDTH = '100%'

# MAIN_CONTROL_PANEL_HEIGHT = '330px'
# MAIN_CONTROL_PANEL_WIDTH = '100%'

# LED_CONTROL_PANEL_HEIGHT = '450px'
# LED_CONTROL_PANEL_WIDTH = '100%'

# REQUIRED_CURRENTS_HEIGHT = '305px'
# REQUIRED_CURRENTS_WIDTH = '600px'

# CHANNEL_CURRENTS_HEIGHT = '39px'
# CHANNEL_CURRENTS_WIDTH = '600px'

# ACTUAL_IRRADIANCES_HEIGHT = '305px'
# ACTUAL_IRRADIANCES_WIDTH = '600px'

# AUDIO_CONTROL_PANEL_HEIGHT = '600px'
# AUDIO_CONTROL_PANEL_WIDTH = '1000px'

INFO_PANEL_HEIGHT = '100%'
INFO_PANEL_WIDTH = '100%'

MAIN_CONTROL_PANEL_HEIGHT = '100%'
MAIN_CONTROL_PANEL_WIDTH = '100%'

LED_CONTROL_PANEL_HEIGHT = '100%'
LED_CONTROL_PANEL_WIDTH = '100%'

REQUIRED_CURRENTS_HEIGHT = '100%'
REQUIRED_CURRENTS_WIDTH = '100%'

CHANNEL_CURRENTS_HEIGHT = '100%'
CHANNEL_CURRENTS_WIDTH = '100%'

ACTUAL_IRRADIANCES_HEIGHT = '100%'
ACTUAL_IRRADIANCES_WIDTH = '100%'

AUDIO_CONTROL_PANEL_HEIGHT = '100%'
AUDIO_CONTROL_PANEL_WIDTH = '100%'

#ACCENT_COLOUR = '#635faa' # purple
ACCENT_COLOUR = '#229abc' # blue
BACKGROUND_COLOUR = '#212121'

css_banner_panel = f"""
<style>
    .banner_panel_css{{
        height : 100%;
        width : 100%;
        overflow : hidden;
    }}
    
    .banner_image_box_css{{
        height : 100%;
        width : 100%;
        overflow : hidden;
    }}
    
    .banner_image_css{{
        border : none;
        overflow : hidden;
    }}
</style>
"""

css_info_panel = f"""
<style>
    .info_panel_css{{
        height : {INFO_PANEL_HEIGHT};
        width : {INFO_PANEL_WIDTH};
        background-color : {BACKGROUND_COLOUR};
    }}
    
    .text_coloured_css{{
        color : {ACCENT_COLOUR};
    }}
    
    .text_css{{
        color : white;
    }}
</style>
"""

css_main_control_panel = f"""
<style>
    .adv_toggle_button{{
    }}
    
    .log{{
        height : 98%;
        width : 100%;
        resize : none;
    }}
    
    .start_button{{
        color : green;
        background-color : #a6a4a4;
    }}
    
    .stop_button{{
        color : red;
        background-color : #a6a4a4;
    }}

    .section_heading{{
        background-color : {ACCENT_COLOUR};
        #border : solid 2px {ACCENT_COLOUR};
        margin : 0;
        #border-left : solid 5px black;
    }}

    .label_setting_box{{
        display : grid;
        grid-template-columns : 50% 40%;
        width : 100%;
    }}

    .main_control_panel_box{{
        display : flex;
        flex-flow : row nowrap;
        height : {MAIN_CONTROL_PANEL_HEIGHT};
        width : {MAIN_CONTROL_PANEL_WIDTH};
        background-color : {BACKGROUND_COLOUR};
    }}
    
    .setup_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 67%;
        #border-top : solid 2px {ACCENT_COLOUR};
        #border-left : solid 2px {ACCENT_COLOUR};
        #border-bottom : solid 2px {ACCENT_COLOUR};
        border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .basic_setup_box{{
        display : flex;
        flex-flow : row nowrap;
        height : 25%;
        width : 100%;
    }}
    
    .advanced_toggle_button_box{{
        display : flex;
        flex-flow : row nowrap;
        height : 15%;
        width : 100%;
        #border-bottom : solid 2px {ACCENT_COLOUR};
    }}
    
    .basic_setup_select_device_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        align-items : flex-start;
        height : 100%;
        width : 100%;
    }}
    
    .basic_setup_bitstream_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        align-items : flex-start;
        height : 100%;
        width : 100%;
    }}
    
    .basic_setup_bitstream_button_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : flex-start;
        align-items : center;
        width : 100%;
    }}
    
    .advanced_setup_box{{
        display : flex;
        flex-flow : row nowrap;
        height : 60%;
        width : 100%;
    }}
    
    .advanced_setup_settings_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        align-items : flex-start;        
        height : 100%;
        width : 50%;
    }}
    
    .advanced_setup_files_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        height : 100%;
        width : 50%;
    }}

    .interact_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;        
        width : 33%;
        #border-top : solid 2px {ACCENT_COLOUR};
        #border-bottom : solid 2px {ACCENT_COLOUR};
        #border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .interact_log_box{{
        height : 60%;
        width : 100%;
    }}
    
    .interact_start_stop_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        align-content : center;
        width : 100%;
    }}

    .led_grid{{
        display : grid;
        grid-template-areas : {'''"00 01 02 03 04 05 06 07 08 09"
                                  "10 11 12 13 14 15 16 17 18 19"
                                  "20 21 22 23 24 25 26 27 28 29"
                                  "30 31 32 33 34 35 36 37 38 39"
                                  "40 41 42 43 44 45 46 47 48 49"
                                  "50 51 52 53 54 55 56 57 58 59"
                                  "60 61 62 63 64 65 66 67 68 69"
                                  "70 71 72 73 74 75 76 77 78 79"
                                  "80 81 82 83 84 85 86 87 88 89"
                                  "90 91 92 93 94 95 96 97 98 99"'''};
        grid-template-rows : repeat(10, 35px);
        grid-template-columns : repeat(10, 35px);
        height : 360px;
        width : 360px;
    }}
    
    .led_grid_loading{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : center;
        align-items : center;
        height : 360px;
        width : 360px;
    }}
    
    .led_indicator{{
        height : 28px;
        width : 28px;
        #background : #c7eef0;
        background : #61747a;
        border-style: inset;
    }}
        
    .led_indicator_clicked{{
        background : #12f3ff;
        border-style : outset;
    }}
    
</style>
"""

css_led_control_panel = f"""
<style>
    .clear_leds_button{{
        color : orange;
    }}
    
    .trigger_signal_box{{
        height : 35px;
        width : 35px;
        background-color : {ACCENT_COLOUR};
    }}

    .trigger_signal_box_on{{
        height : 35px;
        width : 35px;
        background-color : red;
    }}
    
    .peak_irr_select{{
        width : 100%;
    }}
    
    .pulse_duration_select{{
        width : 100%;    
    }}
    
    .pulse_frequency_select{{
        width : 100%;    
    }}
    
    .no_pulses_select{{
        width : 100%;    
    }}
    
    .complex_pattern_text{{
        height : 98%;
        width : 100%;
        resize : none;        
    }}
    
    .led_control_panel{{
        display : flex;
        flex-flow : row nowrap;
        height : {LED_CONTROL_PANEL_HEIGHT};
        width : {LED_CONTROL_PANEL_WIDTH};
        background-color : {BACKGROUND_COLOUR};
    }}
    
    .control_leds_panel{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 35%;
        #border-top : solid 2px {ACCENT_COLOUR};
        #border-left : solid 2px {ACCENT_COLOUR};
        #border-bottom : solid 2px {ACCENT_COLOUR};
        border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .control_leds_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 89%;
        width : 100%;
    }}
    
    .clear_leds_button_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : center;
        align-items : center;
        height : 10%;
        width : 100%;    
    }}
    
    .indicate_leds_panel{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 35%;  
        #border-top : solid 2px {ACCENT_COLOUR};
        #border-bottom : solid 2px {ACCENT_COLOUR};
        border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .indicate_leds_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 90%;
        width : 100%;    
    }}
    
    .trigger_indicator_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : center;
        align-items : center;
        height : 10%;
        width : 100%;
    }}
    
    .led_parameters_panel{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 30%;
        #border-top : solid 2px {ACCENT_COLOUR};
        #border-bottom : solid 2px {ACCENT_COLOUR};
        #border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .config_tab{{
        height : 100%;
        width : 98%;
    }}
    
    .simple_config_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        height : 100%;
        width : 100%;
    }}
    
    .config_setting_box{{
        display : grid;
        grid-template-columns : 55% 35%;
        width : 100%;    
    }}
    
    .complex_config_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        height : 100%;
        width : 100%;
    }}
    
    .config_file_upload_box{{
        display : grid;
        grid-template-columns : 50% 40%;
        height : 15%;
        width : 100%;        
    }}
    
    .config_text_box{{
        height : 85%;
        width : 100%;
    }}
    
</style>
"""

css_array_currents_panel = f"""
<style>
    .required_currents_table{{
        height : {REQUIRED_CURRENTS_HEIGHT};
        width : {REQUIRED_CURRENTS_WIDTH};
        border : solid 1px black;
        margin : none;
        background-color : {BACKGROUND_COLOUR};
    }}
    
    .channel_currents_table{{
        height : {CHANNEL_CURRENTS_HEIGHT};
        width : {CHANNEL_CURRENTS_WIDTH};
        border : solid 1px black;
        margin : none;
        background-color : {BACKGROUND_COLOUR};
    }}
    
    .actual_irradiances_table{{
        height : {ACTUAL_IRRADIANCES_HEIGHT};
        width : {ACTUAL_IRRADIANCES_WIDTH};
        border : solid 1px black;
        margin : none;
        background-color : {BACKGROUND_COLOUR};
    }}    
    
</style>
"""

css_audio_control_panel = f"""
<style>
    #.start_button{{
    #    color : green;
    #}}
    
    #.stop_button{{
    #    color : red;
    #}}
    
    .audio_control_panel{{
        display : flex;
        flex-flow : row nowrap;
        height : {AUDIO_CONTROL_PANEL_HEIGHT};
        width : {AUDIO_CONTROL_PANEL_WIDTH};
    }}
    
    .audio_setup_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 40%;
        border-top : solid 2px {ACCENT_COLOUR};
        border-left : solid 2px {ACCENT_COLOUR};
        border-bottom : solid 2px {ACCENT_COLOUR};
        border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .audio_setup_buttons_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : center;
        align-items : center;
        height : 10%;
        width : 100%;
    }}
    
    .audio_setup_parameters_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 60%;
        width : 100%;
        border-top : solid 2px {ACCENT_COLOUR};
    }}
    
    .audio_plots_settings_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 30%;
        width : 100%;        
        border-top : solid 2px {ACCENT_COLOUR};
    }}
    
    .audio_setup_info_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : space-around;
        height : 0%;
        width : 100%;
    }}

    .audio_plots_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 60%;
        border-top : solid 2px {ACCENT_COLOUR};
        border-bottom : solid 2px {ACCENT_COLOUR};
        border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .plot_box{{
        height : 100%;
        width : 100%;
    }}
    
</style>
"""

css = css_banner_panel + css_info_panel + css_main_control_panel + css_led_control_panel + css_array_currents_panel + css_audio_control_panel
