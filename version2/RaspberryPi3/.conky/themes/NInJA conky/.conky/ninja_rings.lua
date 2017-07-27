--[[
Clock Rings by londonali1010 (2009) , mod by arpinux

This script draws percentage meters as rings, and also draws clock hands if you want! It is fully customisable; all options are described in the script. This script is based off a combination of my clock.lua script and my rings.lua script.

IMPORTANT: if you are using the 'cpu' function, it will cause a segmentation fault if it tries to draw a ring straight away. The if statement on line 145 uses a delay to make sure that this doesn't happen. It calculates the length of the delay by the number of updates since Conky started. Generally, a value of 5s is long enough, so if you update Conky every 1s, use update_num>5 in that if statement (the default). If you only update Conky every 2s, you should change it to update_num>3; conversely if you update Conky every 0.5s, you should use update_num>10. ALSO, if you change your Conky, is it best to use "killall conky; conky" to update it, otherwise the update_num will not be reset and you will get an error.

To call this script in Conky, use the following (assuming that you save this script to ~/scripts/rings.lua):
	lua_load ~/scripts/clock_rings.lua
	lua_draw_hook_pre clock_rings
	
Changelog:
+ v1.0 -- Original release (30.09.2009)
]]

settings_table = {
	{
		name='time',
		arg='%S',
		max=60,
		bg_colour=0x000000,
		bg_alpha=0.4,
		fg_colour=0xADEDE7,
		fg_alpha=0.5,
		x=45, y=50,
		radius=120,
		thickness=15,
		start_angle=130,
		end_angle=200
	},
	{
		name='battery_percent',
		arg='',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0.4,
		fg_colour=0xADEDE7,
		fg_alpha=0.5,
		x=40, y=330,
		radius=30,
		thickness=10,
		start_angle=130,
		end_angle=350
	},
	{
		name='cpu',
		arg='',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0.4,
		fg_colour=0xADEDE7,
		fg_alpha=0.5,
		x=40, y=410,
		radius=30,
		thickness=10,
		start_angle=130,
		end_angle=350
	},
	{
		name='memperc',
		arg='',
		max=100,
		bg_colour=0x000000,
		bg_alpha=0.4,
		fg_colour=0xADEDE7,
		fg_alpha=0.5,
		x=38, y=490,
		radius=30,
		thickness=10,
		start_angle=130,
		end_angle=350
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

function conky_clock_rings()
    local function setup_rings(cr,pt)
        local str=''
        local value=0
        
        str=string.format('${%s %s}',pt['name'],pt['arg'])
        str=conky_parse(str)
        
        value=tonumber(str)
        pct=value/pt['max']
        
        draw_ring(cr,pct,pt)
    end
    
    -- Check that Conky has been running for at least 5s

    if conky_window==nil then return end
    local cs=cairo_xlib_surface_create(conky_window.display,conky_window.drawable,conky_window.visual, conky_window.width,conky_window.height)
    
    local cr=cairo_create(cs)    
    
    local updates=conky_parse('${updates}')
    update_num=tonumber(updates)
    
    if update_num>5 then
        for i in pairs(settings_table) do
            setup_rings(cr,settings_table[i])
        end
    end
end
