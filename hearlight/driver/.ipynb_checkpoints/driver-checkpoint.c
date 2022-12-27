// PYNQ Microblaze driver for HearLight LED control system
// Ryan Greer, University of Strathclyde
// 9th December 2022

#include <gpio.h>
#include <spi.h>
#include <timer.h>
#include <pyprintf.h>
#include <stdint.h>

#define LTC2662_CMD_POWER_DOWN_N 0x40
#define LTC2662_CMD_SPAN 0x60
#define LTC2662_CMD_WRITE_N_UPDATE_N 0x30

spi dac;
gpio cs_a;
gpio cs_b;
gpio trig_out;
gpio switch_handles[10];
int16_t fault_code = 0;
uint32_t max_switch_counts = 0;
uint32_t max_device_counts = 0;
float dac_refs[8] = {3.125, 6.25, 12.5, 25, 50, 100, 200, 300};

/*
Function to transfer block through SPI.
*/
uint8_t dac_write(gpio *cs_handle, uint8_t dac_command, uint8_t selected_dac, uint16_t dac_code){
    // length 3 which corresponds to shorter address of 24 bits
    char tx_array[3];
    char rx_array[3];

    tx_array[0] = dac_command + selected_dac;
    tx_array[1] = (dac_code >> 8) & 0xFF;
    tx_array[2] = dac_code & 0xFF;

    gpio_write(*cs_handle, 0);
    spi_transfer(dac, tx_array, rx_array, 3);
    gpio_write(*cs_handle, 1);
    
    return rx_array[0]; // fault code
}

/*
sets softspan range of all DACs based on 'current_ref'
            'current_ref' sets softspan range (maximum current)
                0 : 3.125 mA
                1 : 6.25 mA
                2 : 12.5 mA
                3 : 25 mA
                4 : 50 mA
                5 : 100 mA
                6 : 200 mA
                7 : 300 mA
*/
uint8_t dac_config(uint8_t channel, uint16_t current_ref){
    uint8_t fault_reg = 0;
    
    uint8_t selected_dac = channel % 5;
    
    uint8_t user_command = 0;
    
    if(current_ref == 0){
        user_command = 1;        
    }
    else if(current_ref == 1){
        user_command = 2;
    }
    else if(current_ref == 2){
        user_command = 3;
    }
    else if(current_ref == 3){
        user_command = 4;
    }
    else if(current_ref == 4){
        user_command = 5;
    }
    else if(current_ref == 5){
        user_command = 6;
    }
    else if(current_ref == 6){
        user_command = 7;
    }
    else if(current_ref == 7){
        user_command = 15;
    }
    
    if((channel >= 0) && (channel < 5)){
        fault_reg |= dac_write(&cs_a, LTC2662_CMD_SPAN, selected_dac, user_command);
    }
    else{
        fault_reg |= dac_write(&cs_b, LTC2662_CMD_SPAN, selected_dac, user_command);
    }

    return fault_reg;
}

/*
Switches on/off DAC channel indicated by 'channel' argument and considers both DACs
            'channel' => 0->9
            'on_off' => '1' is on and '0' is off
            'current_code' => current value in DAC counts
*/
uint8_t dac_channel_control(uint8_t channel, uint8_t on_off, uint16_t current_code){
    uint8_t fault_reg = 0;
    
    uint8_t selected_dac = channel % 5;
    
    if(on_off){
        if((channel >= 0) && (channel < 5)){
            fault_reg |= dac_write(&cs_a, LTC2662_CMD_WRITE_N_UPDATE_N, selected_dac, current_code);
        }
        else{
            fault_reg |= dac_write(&cs_b, LTC2662_CMD_WRITE_N_UPDATE_N, selected_dac, current_code);            
        }
    }
    else{
        if((channel >= 0) && (channel < 5)){
            fault_reg |= dac_write(&cs_a, LTC2662_CMD_POWER_DOWN_N, selected_dac, current_code);
        }
        else{
            fault_reg |= dac_write(&cs_b, LTC2662_CMD_POWER_DOWN_N, selected_dac, current_code);            
        }       
    }
    
    return fault_reg;
}

/*
Opens/closes switches in the switch arrays based on 'sw' argument
            'open_close' = '1' is switch closed and '0' is switch open
*/
void switch_control(gpio *sw, uint8_t open_close){
    if(open_close){
        gpio_write(*sw, 0);     
    }
    else{
        gpio_write(*sw, 1);             
    }
}

/*
Returns 16-bit fault code which indicates which channels have had current corrected due to exceeding limit on system.
10 least significant bits with '1' indicating fault, '0' with no fault, LSB is channel 1 (P1).
*/
int16_t leds_read_fault(){
    return fault_code;
}

/*
Configures DACs and GPIOs for switches, must be called before 'leds_start'
*/
void leds_configure(uint8_t dac_ref, int max_switch_current, int max_device_current){    
    // enable external power supply with en pin connected to A6
    gpio power_supply_en = gpio_open(19);
    gpio_set_direction(power_supply_en, GPIO_OUT);
    gpio_write(power_supply_en, 1);
    
    // RPC handle to control DACs through SPI
    dac = spi_open(13, 12, 11, 17);
    delay_ms(50); // small delay required or first SPI transfers not recognised
    
    // chip select for DAC A and DAC B - initialise to 'high' (slave disabled)
    cs_a = gpio_open(10);
    gpio_set_direction(cs_a, GPIO_OUT);
    gpio_write(cs_a, 1);
    
    cs_b = gpio_open(2);
    gpio_set_direction(cs_b, GPIO_OUT);
    gpio_write(cs_b, 1);
    
    // trigger out signal (pin A3)
    trig_out = gpio_open(16);
    gpio_set_direction(trig_out, GPIO_OUT);
    gpio_write(trig_out, 0);        
    
    // switch array
    uint8_t switch_pins[10] = {3,4,5,6,7,8,9,14,15,16};
    
    for(uint8_t i = 0; i < 10; i++){
        switch_handles[i] = gpio_open(switch_pins[i]);
        gpio_set_direction(switch_handles[i], GPIO_OUT);
        gpio_write(switch_handles[i], 1); // open all switches
    }
    
    // set softspan range for all DACs
    for(uint8_t i = 0; i < 10; i++){
        dac_config(i, dac_ref);
    }
    
    // set maximum switch and device currents in terms of count value
    if(max_switch_current > 130){
        max_switch_current = 130;
    }
    if(max_switch_current < 0){
        max_switch_current = 0;
    }
    max_switch_counts = (uint32_t)((float)max_switch_current / dac_refs[dac_ref] * 65535);
    if(max_switch_counts > 655350){
        max_switch_counts = 655350;
    }
    
    if(max_device_current > 2500){
        max_device_current = 2500;
    }
    if(max_device_current < 0){
        max_device_current = 0;
    }
    max_device_counts = (uint32_t)((float)max_device_current / dac_refs[dac_ref] * 65535);
}

/*
Start LED patterns generating based on alloacted array in DDR memory.
*/
void leds_start(void* led_counts_buffer){
    uint16_t (*led_counts)[10] = (uint16_t (*)[10])led_counts_buffer;
    
    uint16_t row_counts[10] = {0};
    uint32_t row_counts_sum = 0;

    // loop forever
    while(1){
        // loop over all rows
        for(int8_t sw = 0; sw < 10; sw++){
            // set channel currents to zero
            for(uint8_t i = 0; i < 10; i++){
                dac_channel_control(9-i, 0, 0);
            }
            
            // switch off previous row
            if((sw-1) < 0){
                switch_control(&switch_handles[9], 0);
            }
            else{
                switch_control(&switch_handles[sw-1], 0);
            }
            
            // switch on current row
            switch_control(&switch_handles[sw], 1);

            // set channel currents from DDR memory
            row_counts_sum = 0;
            for(uint8_t i = 0; i < 10; i++){
                row_counts_sum += led_counts[sw][i];
            }

            // do not need to check max device current as the switch current check will make sure max device current cannot be exceeded
            if(row_counts_sum > max_switch_counts){
                fault_code = 1023;
                for(uint8_t i = 0; i < 10; i++){
                    row_counts[i] = (uint16_t)((float)max_switch_counts / row_counts_sum * led_counts[sw][i]);
                    dac_channel_control(9-i, 1, row_counts[i]);
                }
            }
            else{
                fault_code = 0;
                for(uint8_t i = 0; i < 10; i++){
                    dac_channel_control(9-i, 1, led_counts[sw][i]);
                }
            }
        }
    }
}
