from pynq.lib import MicroblazeLibrary

LTC2662_CMD_POWER_DOWN_N = 0x40
LTC2662_CMD_SPAN = 0x60
LTC2662_CMD_WRITE_N_UPDATE_N = 0x30

"""Class of high-level functions to control LEDs through electronic control system.

"""
class ControlLEDs():
    def __init__(self, ol):
        lib = MicroblazeLibrary(ol.iop_arduino, ['spi', 'gpio'])
        
        # enable external power supply with en pin connected to A6
        power_supply_en = lib.gpio_open(19)

        power_supply_en.set_direction(lib.GPIO_OUT)
        power_supply_en.write(1)

        # RPC handle to control DACs through SPI
        self.dac = lib.spi_open(13, 12, 11, 17)

        # chip select for DAC A and DAC B - initialise to 'high' (slave disabled)
        self.cs_a = lib.gpio_open(10)
        self.cs_b = lib.gpio_open(2)

        self.cs_a.set_direction(lib.GPIO_OUT)
        self.cs_a.write(1)

        self.cs_b.set_direction(lib.GPIO_OUT)
        self.cs_b.write(1)
        
        # trigger out signal (pin A3)
        self.trig_out = lib.gpio_open(16)
        self.trig_out.set_direction(lib.GPIO_OUT)
        self.trig_out.write(0)
        
        # RPC handle for switches control through GPIO - initialise to 'high' (switch open)
        self.switches = [lib.gpio_open(3),
                         lib.gpio_open(4),
                         lib.gpio_open(5),
                         lib.gpio_open(6),
                         lib.gpio_open(7),
                         lib.gpio_open(8),
                         lib.gpio_open(9),
                         lib.gpio_open(14),
                         lib.gpio_open(15),
                         lib.gpio_open(16)]

        for sw in self.switches:
            sw.set_direction(lib.GPIO_OUT)
            sw.write(1) # low for close switch

    def dac_write(self, cs_handle, dac_command, selected_dac, code):
        """Function to transfer block through SPI.

        """
        tx_array = bytearray(4)
        rx_array = bytearray(4)

        dac_code = bytearray(2)
        dac_code[:] = bytearray(int.to_bytes(code, 2, 'little'))

        tx_array[0] = 0 # first byte is zero
        tx_array[1] = dac_command | selected_dac # command is upper 4 bits, selected DAC is lower 4 bits
        tx_array[2] = dac_code[1]
        tx_array[3] = dac_code[0]

        cs_handle.write(0)
        self.dac.transfer(tx_array, rx_array, 4) # 4 bytes data to read
        cs_handle.write(1)

        fault_reg = rx_array[0]

        return fault_reg
    
    def switch_control(self, sw, open_close):
        """ Opens/closes switches in the switch arrays based on 'sw' argument
            'open_close' = '1' is switch closed and '0' is switch open
        """
        if(open_close):
            self.switches[sw].write(0)
        else:
            self.switches[sw].write(1)

    def dac_config(self, channel, current_ref):
        """ sets softspan range of all DACs based on 'current_ref'
            'current_ref' sets softspan range (maximum current)
                0 : 3.125 mA
                1 : 6.25 mA
                2 : 12.5 mA
                3 : 25 mA
                4 : 50 mA
                5 : 100 mA
                6 : 200 mA
                7 : 300 mA
        """
        fault_reg = 0

        selected_dac = channel % 5

        user_command = 0

        if(current_ref == 0):
            user_command = 1
        elif(current_ref == 1):
            user_command = 2
        elif(current_ref == 2):
            user_command = 3
        elif(current_ref == 3):
            user_command = 4
        elif(current_ref == 4):
            user_command = 5
        elif(current_ref == 5):
            user_command = 6
        elif(current_ref == 6):
            user_command = 7
        elif(current_ref == 7):
            user_command = 15
            
        if(channel >= 0 and channel < 5):
            fault_reg |= self.dac_write(self.cs_a, LTC2662_CMD_SPAN, selected_dac, user_command)
        elif(channel >= 5 and channel < 10):
            fault_reg |= self.dac_write(self.cs_b, LTC2662_CMD_SPAN, selected_dac, user_command)

        return fault_reg

    def dac_channel_control(self, channel, on_off, current_code):
        """ Switches on/off DAC channel indicated by 'channel' argument and considers both DACs
            'channel' => 0->9
            'on_off' => '1' is on and '0' is off
            'current_code' => current value in DAC counts
        """
        fault_reg = 0

        selected_dac = channel % 5

        if(current_code == 0):
            on_off = 0

        dac_code = current_code

        if(on_off):
            if(channel >= 0 and channel < 5):
                fault_reg |= self.dac_write(self.cs_a, LTC2662_CMD_WRITE_N_UPDATE_N, selected_dac, dac_code)
            elif(channel >= 5 and channel < 10):
                fault_reg |= self.dac_write(self.cs_b, LTC2662_CMD_WRITE_N_UPDATE_N, selected_dac, dac_code)            
        else:
            if(channel >= 0 and channel < 5):
                fault_reg |= self.dac_write(self.cs_a, LTC2662_CMD_POWER_DOWN_N, selected_dac, 0)
            elif(channel >= 5 and channel < 10):
                fault_reg |= self.dac_write(self.cs_b, LTC2662_CMD_POWER_DOWN_N, selected_dac, 0)

        return fault_reg
    