# EGo1 manufacturer manual v2.2: SYS_CLK=P17 (100 MHz), LED1_0=K3.
# https://e-elements.readthedocs.io/zh/ego1_v2.2/EGo1.html
set_property PACKAGE_PIN P17 [get_ports clk]
set_property IOSTANDARD LVCMOS33 [get_ports clk]
set_property PACKAGE_PIN K3 [get_ports led]
set_property IOSTANDARD LVCMOS33 [get_ports led]
