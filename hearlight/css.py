MAIN_CONTROL_PANEL_HEIGHT = '330px'
MAIN_CONTROL_PANEL_WIDTH = '1100px'

LED_CONTROL_PANEL_HEIGHT = '500px'
LED_CONTROL_PANEL_WIDTH = '1350px'

ACCENT_COLOUR = '#c7eef0'

css_led_control_panel = f"""
<style>
    .clear_leds_button{{
        color : orange;
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
    }}
    
    .control_leds_panel{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 30%;
    }}
    
    .control_leds_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 80%;
        width : 100%;
    }}
    
    .clear_leds_button_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : flex-start;
        height : 20%;
        width : 100%;    
    }}
    
    .indicate_leds_panel{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 30%;    
    }}
    
    .indicate_leds_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 80%;
        width : 100%;    
    }}
    
    .trigger_indicator_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : center;
        align-items : center;
        height : 20%;
        width : 100%;
    }}
    
    .led_parameters_panel{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 40%;
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
    
    .complex_config_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        height : 100%;
        width : 100%;
    }}
    
    .config_file_upload_box{{
        height : 15%;
        width : 100%;
    }}
    
    .config_text_box{{
        height : 85%;
        width : 100%;
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
    }}
    
    .stop_button{{
        color : red;
    }}

    .section_heading{{
        background-color : {ACCENT_COLOUR};
        #border : solid 2px {ACCENT_COLOUR};
        margin : 0;
        border-left : solid 5px black;
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
    }}
    
    .setup_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 67%;
        border-top : solid 2px {ACCENT_COLOUR};
        border-left : solid 2px {ACCENT_COLOUR};
        border-bottom : solid 2px {ACCENT_COLOUR};
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
        border-bottom : solid 2px {ACCENT_COLOUR};
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
        border-top : solid 2px {ACCENT_COLOUR};
        border-bottom : solid 2px {ACCENT_COLOUR};
        border-right : solid 2px {ACCENT_COLOUR};
    }}
    
    .interact_log_box{{
        height : 60%;
        width : 100%;
    }}
    
    .interact_start_stop_box{{
        display : flex;
        flex-flow : row wrap;
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
        grid-template-rows : repeat(10, 30px);
        grid-template-columns : repeat(10, 30px);
        height : 300px;
        width : 300px;
    }}
    
    .led_indicator{{
        height : 24px;
        width : 24px;
        background : #c7eef0;
        border-style: inset;
    }}
        
    .led_indicator_clicked{{
        background : #12f3ff;
        border-style : outset;
    }}
    
</style>
"""

css = css_main_control_panel + css_led_control_panel
