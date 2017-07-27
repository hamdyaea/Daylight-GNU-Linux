--[[
Ring Meters by londonali1010 (2009)
 
This script draws percentage meters as rings. It is fully customisable; all options are described in the script.
 
IMPORTANT: if you are using the 'cpu' function, it will cause a segmentation fault if it tries to draw a ring straight away. The if statement on line 145 uses a delay to make sure that this doesn't happen. It calculates the length of the delay by the number of updates since Conky started. Generally, a value of 5s is long enough, so if you update Conky every 1s, use update_num > 5 in that if statement (the default). If you only update Conky every 2s, you should change it to update_num > 3; conversely if you update Conky every 0.5s, you should use update_num > 10. ALSO, if you change your Conky, is it best to use "killall conky; conky" to update it, otherwise the update_num will not be reset and you will get an error.
 
To call this script in Conky, use the following (assuming that you save this script to ~/scripts/rings.lua):
	lua_load ~/scripts/rings-v1.2.1.lua
	lua_draw_hook_pre ring_stats
 
Changelog:
+ v1.2.1 -- Fixed minor bug that caused script to crash if conky_parse() returns a nil value (20.10.2009)
+ v1.2 -- Added option for the ending angle of the rings (07.10.2009)
+ v1.1 -- Added options for the starting angle of the rings, and added the "max" variable, to allow for variables that output a numerical value rather than a percentage (29.09.2009)
+ v1.0 -- Original release (28.09.2009)
]]
 
settings_table = {
	--[[   ###############  CLOCKWISE ##########]]--
			--[[   ############### CIRCLES CLOCK ]]--
			--[[   ############### DATE  - Structure: plate, circle, circle]]--
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xd0d0d0,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=90, y=142,
		radius=20,
		thickness=40,
		start_angle=0,
		end_angle=360
	},
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=90, y=142,
		radius=41,
		thickness=3,
		start_angle=0,
		end_angle=360
	},
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=90, y=142,
		radius=42,
		thickness=2,
		start_angle=0,
		end_angle=360
	},
				--[[   ###############  MINUTES  - Structure: plate, circle, circle]]--
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=122, y=102,
		radius=20,
		thickness=40,
		start_angle=-0,
		end_angle=360
	},
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=122, y=102,
		radius=41,
		thickness=3,
		start_angle=-20,
		end_angle=170
	},
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=122, y=102,
		radius=42,
		thickness=2,
		start_angle=-20,
		end_angle=167
		},
				--[[   ###############  HOURS - Structure: plate, circle, circle]]--
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xf6f6f6,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=70, y=82,
		radius=20,
		thickness=40,
		start_angle=-0,
		end_angle=360
	},
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=70, y=82,
		radius=41,
		thickness=3,
		start_angle=198,
		end_angle=426
	},
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xe8e8e8,
		bg_alpha=1,
		fg_colour=0x000000,
		fg_alpha=0,
		x=70, y=82,
		radius=42,
		thickness=2,
		start_angle=202,
		end_angle=423
	},
			--[[   ############### CIRCLE ROOT  ]]--
			--[[   ############### CIRCLE ROOT  - Structure:  plate, graph]]--
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xffffff,
		bg_alpha=0.3,
		fg_colour=0x000000,
		fg_alpha=0,
		x=240, y=100,
		radius=20,
		thickness=40,
		start_angle=-0,
		end_angle=360
	},
	{
		name='fs_used_perc',
		arg='/',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0.1,
		fg_colour=0x000000,
		fg_alpha=0.2,
		x=240, y=100,
		radius=40,
		thickness=4,
		start_angle=-30,
		end_angle=330
	},
			--[[   ############### CIRCLE MEM  ]]--
			--[[   ############### CIRCLE MEM  - Structure:  plate, graph]]--
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xffffff,
		bg_alpha=0.3,
		fg_colour=0x000000,
		fg_alpha=0,
		x=180, y=200,
		radius=20,
		thickness=40,
		start_angle=-0,
		end_angle=360
	},
	{
		name='memperc',
		arg='',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0.1,
		fg_colour=0x000000,
		fg_alpha=0.2,
		x=180, y=200,
		radius=40,
		thickness=4,
		start_angle=20,
		end_angle=380
	},
}
settings_t = {
		--[[   ###############  COUNTERCLOCKWISE ##########]]--
			--[[   ############### CIRCLE CPUS ]]--
			--[[   ############### CIRCLE CPUS - Structure: plate,  cpu0-4, outer ring is defined by cpu0 ]]--	
	{
		name='time',
		arg='%I',
		max=100,
		bg_colour=0xffffff,
		bg_alpha=0.3,
		fg_colour=0x000000,
		fg_alpha=0,
		x=70, y=240,
		radius=20,
		thickness=40,
		start_angle=-30,
		end_angle=-390
	},
	{
		name='cpu',
		arg='cpu0',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0.1,
		fg_colour=0x000000,
		fg_alpha=0.1,
		x=70, y=240,
		radius=40,
		thickness=4,
		start_angle=-30,
		end_angle=-390
	},
	{
		name='cpu',
		arg='cpu1',
		max=100,
		bg_colour=0xffffff,
		bg_alpha=0,
		fg_colour=0x000000,
		fg_alpha=0.1,
		x=70, y=240,
		radius=40,
		thickness=4,
		start_angle=-30,
		end_angle=-390
	},
	{
		name='cpu',
		arg='cpu2',
		max=100,
		bg_colour=0xffffff,
		bg_alpha=0,
		fg_colour=0x000000,
		fg_alpha=0.1,
		x=70, y=240,
		radius=40,
		thickness=4,
		start_angle=-30,
		end_angle=-390
	},
	{
		name='cpu',
		arg='cpu3',
		max=100,
		bg_colour=0xffffff,
		bg_alpha=0,
		fg_colour=0x000000,
		fg_alpha=0.1,
		x=70, y=240,
		radius=40,
		thickness=4,
		start_angle=-30,
		end_angle=-390
	},
			--[[   ############### CIRCLE BAT  ]]--
			--[[   ############### CIRCLE BAT - Structure:  plate, graph]]--
	{
		name='battery_percent',
		arg='BAT1',
		max=1,
		bg_colour=0xffffff,
		bg_alpha=0,
		fg_colour=0xffffff,
		fg_alpha=0.3,
		x=140, y=340,
		radius=20,
		thickness=40,
		start_angle=0,
		end_angle=-360
	},
	{
		name='battery_percent',
		arg='BAT1',
		max=1,
		bg_colour=0x000000,
		bg_alpha=0,
		fg_colour=0x000000,
		fg_alpha=0.1,
		x=140, y=340,
		radius=40,
		thickness=4,
		start_angle=80,
		end_angle=-440
	},
	{
		name='battery_percent',
		arg='BAT1',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0,
		fg_colour=0x000000,
		fg_alpha=0.2,
		x=140, y=340,
		radius=40,
		thickness=4,
		start_angle=235,
		end_angle=-125
	},
} 
require 'cairo'
 
function rgb_to_r_g_b(colour,alpha)
	return ((colour / 0x10000) % 0x100) / 255., ((colour / 0x100) % 0x100) / 255., (colour % 0x100) / 255., alpha
end
 
function draw_ring(cr,t,pt)
	local w,h=conky_window.width,conky_window.height
 
	local xc,yc,ring_r,ring_w,sa,ea=pt['x'],pt['y'],pt['radius'],pt['thickness'],pt['start_angle'],pt['end_angle']
	local bgc, bga, fgc, fga=pt['bg_colour'], pt['bg_alpha'], pt['fg_colour'], pt['fg_alpha']
 
	local angle_0=sa*(2*math.pi/360)-math.pi/2
	local angle_f=ea*(2*math.pi/360)-math.pi/2
	local t_arc=t*(angle_f-angle_0)
 
	-- Draw background ring
 
	cairo_arc(cr,xc,yc,ring_r,angle_0,angle_f)
	cairo_set_source_rgba(cr,rgb_to_r_g_b(bgc,bga))
	cairo_set_line_width(cr,ring_w)
	cairo_stroke(cr)
 
	-- Draw indicator ring
 
	cairo_arc(cr,xc,yc,ring_r,angle_0,angle_0+t_arc)
	cairo_set_source_rgba(cr,rgb_to_r_g_b(fgc,fga))
	cairo_stroke(cr)		
end
function draw_ring_cc(cr,t,pt)
	local w,h=conky_window.width,conky_window.height
 
	local xc,yc,ring_r,ring_w,sa,ea=pt['x'],pt['y'],pt['radius'],pt['thickness'],pt['start_angle'],pt['end_angle']
	local bgc, bga, fgc, fga=pt['bg_colour'], pt['bg_alpha'], pt['fg_colour'], pt['fg_alpha']
 
	local angle_0=sa*(2*math.pi/360)-math.pi/2
	local angle_f=ea*(2*math.pi/360)-math.pi/2
	local t_arc=t*(angle_f-angle_0)
 
	-- Draw background ring
 
	cairo_arc_negative(cr,xc,yc,ring_r,angle_0,angle_f)
	cairo_set_source_rgba(cr,rgb_to_r_g_b(bgc,bga))
	cairo_set_line_width(cr,ring_w)
	cairo_stroke(cr)
 
	-- Draw indicator ring
 
	cairo_arc_negative(cr,xc,yc,ring_r,angle_0,angle_0+t_arc)
	cairo_set_source_rgba(cr,rgb_to_r_g_b(fgc,fga))
	cairo_stroke(cr)		
end 
function conky_ring_stats()
	local function setup_rings(cr,pt)
		local str=''
		local value=0
 
		str=string.format('${%s %s}',pt['name'],pt['arg'])
		str=conky_parse(str)
 
		value=tonumber(str)
		if value == nil then value = 0 end
		pct=value/pt['max']
 
		draw_ring(cr,pct,pt)
	end
	local function setup_rings_cc(cr,pt)
		local str=''
		local value=0
 
		str=string.format('${%s %s}',pt['name'],pt['arg'])
		str=conky_parse(str)
 
		value=tonumber(str)
		if value == nil then value = 0 end
		pct=value/pt['max']
 
		draw_ring_cc(cr,pct,pt)
	end 
	if conky_window==nil then return end
	local cs=cairo_xlib_surface_create(conky_window.display,conky_window.drawable,conky_window.visual, conky_window.width,conky_window.height)
 
	local cr=cairo_create(cs)	
 
	local updates=conky_parse('${updates}')
	update_num=tonumber(updates)
 
	if update_num>5 then
		for i in pairs(settings_table) do
			setup_rings(cr,settings_table[i])
		end
		for i in pairs(settings_t) do
			setup_rings_cc(cr,settings_t[i])
		end
	end
end
