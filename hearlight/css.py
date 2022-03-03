MAIN_CONTROL_PANEL_HEIGHT = '350px'

css = f"""
<style>
    .label_setting_box{{
        display : grid;
        grid-template-columns : 50% 40%;
        width : 100%;
    }}

    .main_control_panel_box{{
        display : flex;
        flex-flow : row nowrap;
        height : {MAIN_CONTROL_PANEL_HEIGHT};
        width : 100%;
    }}
    
    .setup_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;
        width : 50%;
    }}
    
    .basic_setup_box{{
        display : flex;
        flex-flow : row nowrap;
        height : 33%;
        width : 100%;
    }}
    
    .basic_setup_select_device_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        align-items : center;
        height : 100%;
        width : 100%;
    }}
    
    .basic_setup_bitstream_box{{
        display : flex;
        flex-flow : column nowrap;
        justify-content : flex-start;
        align-items : center;
        height : 100%;
        width : 100%;
    }}
    
    .basic_setup_bitstream_button_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : space-around;
        align-items : center;
        width : 100%;
    }}
    
    .advanced_setup_box{{
        display : flex;
        flex-flow : row nowrap;
        height : 66%;
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
        align-items : center;        
        height : 100%;
        width : 50%;
    }}
    
    .advanced_setup_irr_to_current_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : space-around;
        align-items : center;
        width : 100%;
    }}

    .advanced_setup_current_to_irr_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : space-around;
        align-items : center;
        width : 100%;
    }}

    .interact_box{{
        display : flex;
        flex-flow : column nowrap;
        height : 100%;        
        width : 50%;
    }}
    
    .interact_irr_trigger_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : space-around;
        align-items : center;
        width : 100%;
    }}
    
    .interact_start_stop_box{{
        display : flex;
        flex-flow : row nowrap;
        justify-content : space-around;
        align-items : center;
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
        grid-template-rows : repeat(10, 40px);
        grid-template-columns : repeat(10, 40px);
        height : 400px;
        width : 400px;
    }}
    
    .led_indicator{{
        height : 34px;
        width : 34px;
        background : #c7eef0;
        border-style: inset;
    }}
        
    .led_indicator_clicked{{
        background : #12f3ff;
        border-style : outset;
    }}
    
</style>
"""
