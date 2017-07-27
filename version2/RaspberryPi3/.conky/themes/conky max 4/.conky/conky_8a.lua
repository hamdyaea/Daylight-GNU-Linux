--[[ RINGS with SECTORS widget
	v1.1 by wlourf (07 Jan. 2011)
	edited by Caymus
	this widget draws a ring with differents effects 
	http://u-scripts.blogspot.com/2010/08/rings-sectors-widgets.html
	
To call the script in a conky, use, before TEXT
	lua_load /path/to/the/script/rings.lua
	lua_draw_hook_pre main_rings
and add one line (blank or not) after TEXT


Parameters are :
3 parameters are mandatory
name		- the name of the conky variable to display,
			  for example for {$cpu cpu0}, just write name="cpu"
arg			- the argument of the above variable,
			  for example for {$cpu cpu0}, just write arg="cpu0"
		  	  arg can be a numerical value if name=""
max			- the maximum value the above variable can reach,
			  for example for {$cpu cpu0}, just write max=100
	
Optional parameters:
xc,yc		- coordinates of the center of the ring,
			  default = middle of the conky window
radius		- external radius of the ring, in pixels,
			  default = quarter of the width of the conky window
thickness	- thickness of the ring, in pixels, default = 10 pixels
start_angle	- starting angle of the ring, in degrees, value can be negative,
			  default = 0 degree
end_angle	- ending angle of the ring, in degrees,
			  value must be greater than start_angle, default = 360 degrees
sectors		- number of sectors in the ring, default = 10
gap_sectors - gap between two sectors, in pixels, default = 1 pixel
cap			- the way to close a sector, available values are
				"p" for parallel , default value 
				"r" for radial (follow the radius)
inverse_arc	- if set to true, arc will be anticlockwise, default=false
border_size	- size of the border, in pixels, default = 0 pixel i.e. no border
fill_sector	- if set to true, each sector will be completely filled,
			  default=false, this parameter is inoperate if sectors=1
background	- if set to false, background will not be drawn, default=true
foreground	- if set to false, foreground will not be drawn, default=true

Colours tables below are defined into braces :
{position in the gradient (0 to 1), colour in hexadecimal, alpha (0 to 1)}
example for a single colour table : 
{{0,0xFFAA00,1}} position parameter doesn't matter
example for a two-colours table : 
{{0,0xFFAA00,1},{1,0x00AA00,1}} or {{0.5,0xFFAA00,1},{1,0x00AA00,1}}
example for a three-colours table : 
{{0,0xFFAA00,1},{0.5,0xFF0000,1},{1,0x00AA00,1}}

bg_colour1	- colour table for background,
			  default = {{0,0x00ffff,0.1},{0.5,0x00FFFF,0.5},{1,0x00FFFF,0.1}}
fg_colour1	- colour table for foreground,
			  default = {{0,0x00FF00,0.1},{0.5,0x00FF00,1},{1,0x00FF00,0.1}}
bd_colour1	- colour table for border,
			  default = {{0,0xFFFF00,0.5},{0.5,0xFFFF00,1},{1,0xFFFF00,0.5}}			  

Seconds tables for radials gradients :
bg_colour2	- second colour table for background, default = no second colour
fg_colour2	- second colour table for foreground, default = no second colour
bd_colour2	- second colour table for border, default = no second colour

draw_me     - if set to false, text is not drawn (default = true or 1)
              it can be used with a conky string, if the string returns 1, the text is drawn :
              example : "${if_empty ${wireless_essid wlan0}}${else}1$endif",

v1.0 (08 Aug. 2010) original release
v1.1 (07 Jan. 2011) Add draw_me parameter and correct memory leaks, thanks to "Creamy Goodness"
                    text is parsed inside the function, not in the array of settings

--      This program is free software; you can redistribute it and/or modify
--      it under the terms of the GNU General Public License as published by
--      the Free Software Foundation version 3 (GPLv3)
--     
--      This program is distributed in the hope that it will be useful,
--      but WITHOUT ANY WARRANTY; without even the implied warranty of
--      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
--      GNU General Public License for more details.
--     
--      You should have received a copy of the GNU General Public License
--      along with this program; if not, write to the Free Software
--      Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston,
--      MA 02110-1301, USA.		

]]


require 'cairo'

function conky_main_rings()
-- START PARAMETERS HERE
local rings_settings={

        {
        name="cpu",
        arg="cpu1",
        max=100,
        xc=60,
        yc=150,
        radius=60,
        thickness=10,
        start_angle=-120,
        end_angle=120,
        sectors=20,
        bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
      name="cpu",
        arg="cpu2",
        max=100,
        xc=60,
        yc=150,
        radius=50,
        thickness=10,
        start_angle=-120,
        end_angle=120,
        sectors=20,
        bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="memperc",
	arg="",
	max=100,
	xc=200,
	yc=150,
	thickness=10,
        radius=60,
        thickness=10,
        start_angle=-120,
        end_angle=120,
        sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="swapperc",
	arg="",
	max=100,
	xc=200,
	yc=150,
	thickness=10,
        radius=50,
        thickness=10,
        start_angle=-120,
        end_angle=120,
        sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="fs_used_perc",
	arg="/",
	max=100,
	xc=60,
	yc=270,
	thickness=10,
	radius=60,
	start_angle=275,
	end_angle=445,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="fs_used_perc",
	arg="/home",
	max=100,
	xc=60,
	yc=270,
	thickness=10,
	radius=60,
	start_angle=95,
	end_angle=265,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
        },

	{
	name="fs_used_perc",
	arg="/media/Data",
	max=100,
	xc=200,
	yc=270,
	thickness=10,
	radius=60,
	start_angle=275,
	end_angle=445,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="fs_used_perc",
	arg="/media/VM",
	max=100,
	xc=200,
	yc=270,
	thickness=10,
	radius=60,
	start_angle=95,
	end_angle=265,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="downspeedf",
	arg="ppp0",
	max=100,
	xc=130,
	yc=450,
	thickness=10,
	radius=100,
	start_angle=275,
	end_angle=445,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="upspeedf",
	arg="ppp0",
	max=100,
	xc=130,
	yc=450,
	thickness=10,
	radius=100,
	start_angle=95,
	end_angle=265,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="downspeedf",
	arg="eth0",
	max=100,
	xc=130,
	yc=450,
	thickness=10,
	radius=110,
	start_angle=275,
	end_angle=445,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="upspeedf",
	arg="eth0",
	max=100,
	xc=130,
	yc=450,
	thickness=10,
	radius=110,
	start_angle=95,
	end_angle=265,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="downspeedf",
	arg="wlan0",
	max=100,
	xc=130,
	yc=450,
	thickness=10,
	radius=120,
	start_angle=275,
	end_angle=445,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

	{
	name="upspeedf",
	arg="wlan0",
	max=100,
	xc=130,
	yc=450,
	thickness=10,
	radius=120,
	start_angle=95,
	end_angle=265,
	sectors=20,
	bg_colour1={{0,0x999999,0},{0.5,0x999999,1}, {1,0x999999,0}},
        fg_colour1={{0,0XffFF00,0},{0.5,0xffFF00,1}, {1,0xffFF00,0}},
        fg_colour2={{0,0XFF0000,0},{0.5,0xFF0000,1}, {1,0xFF0000,0}},
	},

}
--END OF PARAMETERS HERE

--main function

	if conky_window==nil then return end

	local cs=cairo_xlib_surface_create(conky_window.display,
		conky_window.drawable, 
		conky_window.visual, conky_window.width, conky_window.height)
	local cr=cairo_create(cs)

	if tonumber(conky_parse('${updates}'))>3 then
		for i in pairs(rings_settings) do
			draw_ring(cr,rings_settings[i])
		end
	end

	cairo_destroy(cr)

end




function draw_ring(cr, t)

	local function rgba_to_r_g_b_a(tcolour)
		local colour,alpha=tcolour[2],tcolour[3]
		return ((colour / 0x10000) % 0x100) / 255., 
			((colour / 0x100) % 0x100) / 255., (colour % 0x100) / 255., alpha
	end
			
			
	local function calc_delta(tcol1,tcol2)
		--calculate deltas P R G B A to table_colour 1

		for x = 1, #tcol1 do
			tcol1[x].dA	= 0
			tcol1[x].dP = 0
	 		tcol1[x].dR = 0
			tcol1[x].dG = 0
			tcol1[x].dB = 0
			if tcol2~=nil and #tcol1 == #tcol2 then
				local r1,g1,b1,a1 = rgba_to_r_g_b_a(tcol1[x])
				local r2,g2,b2,a2 = rgba_to_r_g_b_a(tcol2[x])
				tcol1[x].dP = (tcol2[x][1]-tcol1[x][1])/t.sectors
		 		tcol1[x].dR = (r2-r1)/t.sectors
				tcol1[x].dG = (g2-g1)/t.sectors
				tcol1[x].dB = (b2-b1)/t.sectors
				tcol1[x].dA = (a2-a1)/t.sectors		
				
			end
		end
		
		return tcol1
	end

	--check values
	local function setup(t)
		if t.name==nil and t.arg==nil then 
			print ("No input values ... use parameters 'name'" +
				" with 'arg' or only parameter 'arg' ") 
			return
		end

		if t.max==nil then
			print ("No maximum value defined, use 'max'")
			print ("for name=" .. t.name)
			print ("with arg=" .. t.arg)
			return
		end
		if t.name==nil then t.name="" end
		if t.arg==nil then t.arg="" end

		if t.xc==nil then t.xc=conky_window.width/2 end
		if t.yc==nil then t.yc=conky_window.height/2 end
		if t.thickness ==nil then t.thickness = 10 end
		if t.radius ==nil then t.radius =conky_window.width/4 end
		if t.start_angle==nil then t.start_angle =0 end
		if t.end_angle==nil then t.end_angle=360 end
		if t.bg_colour1==nil then 
			t.bg_colour1={{0,0x00ffff,0.1},{0.5,0x00FFFF,0.5},{1,0x00FFFF,0.1}}
		end
		if t.fg_colour1==nil then
			t.fg_colour1={{0,0x00FF00,0.1},{0.5,0x00FF00,1},{1,0x00FF00,0.1}}
		end
		if t.bd_colour1==nil then
			t.bd_colour1={{0,0xFFFF00,0.5},{0.5,0xFFFF00,1},{1,0xFFFF00,0.5}}
		end
		if t.sectors==nil then t.sectors=10 end
		if t.gap_sectors==nil then t.gap_sectors=1 end 
		if t.fill_sector==nil then t.fill_sector=false end
		if t.sectors==1 then t.fill_sector=false end
		if t.border_size==nil then t.border_size=0 end
		if t.cap==nil then t.cap="p" end
		--some checks
		if t.thickness>t.radius then t.thickness=t.radius*0.1 end
		t.int_radius = t.radius-t.thickness

		--check colors tables 
		for i=1, #t.bg_colour1 do 
			if #t.bg_colour1[i]~=3 then t.bg_colour1[i]={1,0xFFFFFF,0.5} end
		end
		for i=1, #t.fg_colour1 do 
			if #t.fg_colour1[i]~=3 then t.fg_colour1[i]={1,0xFF0000,1} end
		end
		for i=1, #t.bd_colour1 do 
			if #t.bd_colour1[i]~=3 then t.bd_colour1[i]={1,0xFFFF00,1} end
		end
	
		if t.bg_colour2~=nil then
			for i=1, #t.bg_colour2 do 
				if #t.bg_colour2[i]~=3 then t.bg_colour2[i]={1,0xFFFFFF,0.5} end
			end
		end
		if t.fg_colour2~=nil then
			for i=1, #t.fg_colour2 do 
				if #t.fg_colour2[i]~=3 then t.fg_colour2[i]={1,0xFF0000,1} end
			end
		end
		if t.bd_colour2~=nil then
			for i=1, #t.bd_colour2 do 
				if #t.bd_colour2[i]~=3 then t.bd_colour2[i]={1,0xFFFF00,1} end
			end
		end 	
		
		if t.start_angle>=t.end_angle then
		 local tmp_angle=t.end_angle
		 t.end_angle= t.start_angle
		 t.start_angle = tmp_angle
		 -- print ("inversed angles")
			if t.end_angle-t.start_angle>360 and t.start_angle>0 then
				t.end_angle=360+t.start_angle
				print ("reduce angles")
			end
		
			if t.end_angle+t.start_angle>360 and t.start_angle<=0 then
				t.end_angle=360+t.start_angle
				print ("reduce angles")
			end
		
			if t.int_radius<0 then t.int_radius =0 end
			if t.int_radius>t.radius then
				local tmp_radius=t.radius
				t.radius=t.int_radius
				t.int_radius=tmp_radius
				print ("inversed radius")
			end
			if t.int_radius==t.radius then
				t.int_radius=0
				print ("int radius set to 0")
			end 
		end
		
		t.fg_colour1 = calc_delta(t.fg_colour1,t.fg_colour2)
		t.bg_colour1 = calc_delta(t.bg_colour1,t.bg_colour2)
		t.bd_colour1 = calc_delta(t.bd_colour1,t.bd_colour2)
	end
	
	if t.draw_me == true then t.draw_me = nil end
	if t.draw_me ~= nil and conky_parse(tostring(t.draw_me)) ~= "1" then return end	
	--initialize table
	setup(t)
	
	--initialize cairo context
	cairo_save(cr)
	cairo_translate(cr,t.xc,t.yc)
	cairo_set_line_join (cr, CAIRO_LINE_JOIN_ROUND)
	cairo_set_line_cap (cr, CAIRO_LINE_CAP_ROUND)

	--get value
	local value = 0
	if t.name ~="" then
		value = tonumber(conky_parse(string.format('${%s %s}', t.name, t.arg)))
	else
		value = tonumber(t.arg)
	end
	if value==nil then value =0 end

	--initialize sectors
	--angle of a sector :
	local angleA = ((t.end_angle-t.start_angle)/t.sectors)*math.pi/180
	--value of a sector : 
	local valueA = t.max/t.sectors
	--first angle of a sector : 
	local lastAngle = t.start_angle*math.pi/180


	local function draw_sector(type_arc,angle0,angle,valpc, idx)
	 
		--this function draws a portion of arc
	 	--type of arc, angle0 = strating angle, angle= angle of sector,
	 	--valpc = percentage inside the sector, idx = sctor number #
	 	local tcolor
		 if type_arc=="bg" then 		--background
			 if valpc==1 then return end
		 	tcolor=t.bg_colour1
		 elseif type_arc=="fg" then	--foreground
		 	if valpc==0 then return end
		 	tcolor=t.fg_colour1
		 elseif type_arc=="bd" then	--border
		 	tcolor=t.bd_colour1
		 end 

		--angles equivalents to gap_sector
		local ext_delta=math.atan(t.gap_sectors/(2*t.radius))
		local int_delta=math.atan(t.gap_sectors/(2*t.int_radius))

		--angles of arcs
		local ext_angle=(angle-ext_delta*2)*valpc
		local int_angle=(angle-int_delta*2)*valpc

		--define colours to use for this sector
		if #tcolor==1 then 
			--plain color
			local vR,vG,vB,vA = rgba_to_r_g_b_a(tcolor[1])
			cairo_set_source_rgba(cr,vR+tcolor[1].dR*idx,
									vG+tcolor[1].dG*idx,
									vB+tcolor[1].dB*idx,
									vA+tcolor[1].dA*idx	)
		else
			--radient color
			local pat=cairo_pattern_create_radial(0,0,t.int_radius,0,0,t.radius)
			for i=1, #tcolor do
				local vP,vR,vG,vB,vA = tcolor[i][1], rgba_to_r_g_b_a(tcolor[i])
				cairo_pattern_add_color_stop_rgba (pat, 
									vP+tcolor[i].dP*idx,
									vR+tcolor[i].dR*idx,
									vG+tcolor[i].dG*idx,
									vB+tcolor[i].dB*idx,
									vA+tcolor[i].dA*idx	)
			end
			cairo_set_source (cr, pat)
			cairo_pattern_destroy(pat)
		end

		--start drawing
		 cairo_save(cr)
		--x axis is parrallel to start of sector
		cairo_rotate(cr,angle0-math.pi/2)

		local ri,re = t.int_radius ,t.radius

		--point A 
		local angle_a
	
		if t.cap == "p" then 
			angle_a = int_delta
			if t.inverse_arc and type_arc ~="bg" then
				angle_a = angle-int_angle-int_delta
			end
			if not(t.inverse_arc) and type_arc =="bg" then
				angle_a = int_delta+int_angle
			end
		else --t.cap=="r"
			angle_a = ext_delta
			if t.inverse_arc and type_arc~="bg" then
				angle_a = angle-ext_angle-ext_delta
			end
			if not(t.inverse_arc) and type_arc=="bg" then
				angle_a = ext_delta+ext_angle
			end
		end
		local ax,ay = ri*math.cos(angle_a),ri*math.sin(angle_a)


		--point B
		local angle_b = ext_delta
		if t.cap == "p" then 
			if t.inverse_arc and type_arc ~="bg" then
				angle_b = angle-ext_angle-ext_delta
			end
			if not(t.inverse_arc) and type_arc=="bg" then
				angle_b = ext_delta+ext_angle
			end
		else
			if t.inverse_arc and type_arc ~="bg" then
				angle_b = angle-ext_angle-ext_delta
			end
			if not(t.inverse_arc) and type_arc=="bg" then
				angle_b = ext_delta+ext_angle
			end
		end
		local bx,by = re*math.cos(angle_b),re*math.sin(angle_b)

		-- EXTERNAL ARC B --> C
		local b0,b1
		if t.inverse_arc then
			if type_arc=="bg" then
				b0,b1= ext_delta, angle-ext_delta-ext_angle
			else
				b0,b1= angle-ext_angle-ext_delta, angle-ext_delta
			end
		else
			if type_arc=="bg" then
				b0,b1= ext_delta+ext_angle, angle-ext_delta
			else
				b0,b1= ext_delta, ext_angle+ext_delta
			end
		end
		
		---POINT D
		local angle_c, angle_d
		if t.cap == "p" then 
			angle_d = angle-int_delta
			if t.inverse_arc and type_arc=="bg" then
				angle_d = angle-int_delta-int_angle	
			end
			if not(t.inverse_arc) and type_arc~="bg" then
				angle_d=int_delta+int_angle
			end
		else
			angle_d = angle-ext_delta
			if t.inverse_arc and type_arc=="bg" then
				angle_d =angle-ext_delta-ext_angle
			end
			if not(t.inverse_arc) and type_arc~="bg" then
				angle_d = ext_angle+ext_delta
			end
		end
		local dx,dy = ri*math.cos(angle_d),ri*math.sin(angle_d)
		
		-- INTERNAL ARC D --> A
		local d0,d1
		if t.cap=="p" then	
			if t.inverse_arc then	
				if type_arc=="bg" then
					d0,d1= angle-int_delta-int_angle,int_delta
				else
					d0,d1= angle-int_delta, angle- int_angle-int_delta
				end
			else
				if type_arc=="bg" then
					d0,d1= angle-int_delta, int_delta+int_angle
				else
					d0,d1= int_delta+int_angle, int_delta
				end
			end
		else
			if t.inverse_arc then	
				if type_arc=="bg" then	
					d0,d1= angle-ext_delta-ext_angle,ext_delta
				else
					d0,d1= angle-ext_delta, angle- ext_angle-ext_delta
				end
			else
				if type_arc=="bg" then	
					d0,d1= angle-ext_delta,ext_delta+ext_angle
				else	
					d0,d1= ext_angle+ext_delta, ext_delta
				end
			end			
		end
			
		--draw sector
		cairo_move_to(cr,ax,ay)
		cairo_line_to(cr,bx,by)
		cairo_arc(cr,0,0,re,b0,b1)
		cairo_line_to(cr,dx,dy) 
		cairo_arc_negative(cr,0,0,ri,d0,d1)
		 cairo_close_path (cr);

		--stroke or fill sector
		 if type_arc=="bd" then
		 	cairo_set_line_width(cr,t.border_size)
		 	cairo_stroke(cr)
		 else
			 cairo_fill(cr)
		 end

		 cairo_restore(cr)

	 end
	--draw sectors
	local n0,n1,n2 = 1,t.sectors,1
	if t.inverse_arc then n0,n1,n2 = t.sectors,1,-1 end
	local index = 0
	for i = n0,n1,n2 do 
		index = index +1
		local valueZ=1
		local cstA, cstB = (i-1),i
		if t.inverse_arc then cstA,cstB = (t.sectors-i), (t.sectors-i+1) end
		
		if value>valueA *cstA and value<valueA*cstB then
			if not t.fill_sector then
				valueZ = (value-valueA*cstA)/valueA
			end
		else
			if value<valueA*cstB then valueZ=0 end
		end
		
		local start_angle= lastAngle+(i-1)*angleA
		if t.foreground ~= false then 
			draw_sector("fg",start_angle,angleA,valueZ, index)
		end
		if t.background ~= false then 
			draw_sector("bg",start_angle,angleA,valueZ, i)
		end
		if t.border_size>0 then draw_sector("bd",start_angle,angleA,1, i) end
	end

	cairo_restore(cr)
end


--[[END OF RING-SECTORS WIDGET]]

require 'cairo'
    
function conky_main_box()

    if conky_window==nil then return end

	---------------------- PARAMETERS BEGIN HERE
    local boxes_settings={
    --FIRST COLUMN
        --default colour and corner

    }


    ---------------------------- PARAMETERS END HERE
    
    local cs=cairo_xlib_surface_create(conky_window.display, conky_window.drawable, conky_window.visual, conky_window.width, conky_window.height)
    local cr=cairo_create(cs)
    
    if tonumber(conky_parse("$updates"))<5 then return end
    for i in pairs(boxes_settings) do
        draw_box (cr,boxes_settings[i])
    end
    cairo_destroy(cr)
    cairo_surface_destroy(cs)    
end

    
function draw_box(cr,t)

	if t.draw_me == true then t.draw_me = nil end
	if t.draw_me ~= nil and conky_parse(tostring(t.draw_me)) ~= "1" then return end	

    local table_corners={"circle","curve","line"}

    local t_operators={
        clear   = CAIRO_OPERATOR_CLEAR,
        source  = CAIRO_OPERATOR_SOURCE,
        over    = CAIRO_OPERATOR_OVER,
        ["in"]      = CAIRO_OPERATOR_IN,
        out     = CAIRO_OPERATOR_OUT,
        atop    = CAIRO_OPERATOR_ATOP,
        dest    = CAIRO_OPERATOR_DEST,
        dest_over   = CAIRO_OPERATOR_DEST_OVER,
        dest_in = CAIRO_OPERATOR_DEST_IN,
        dest_out = CAIRO_OPERATOR_DEST_OUT,
        dest_atop = CAIRO_OPERATOR_DEST_ATOP,
        xor = CAIRO_OPERATOR_XOR,
        add = CAIRO_OPERATOR_ADD,
        saturate =  CAIRO_OPERATOR_SATURATE,
    }
        
    function rgba_to_r_g_b_a(tc)
        --tc={position,colour,alpha}
        local colour = tc[2]
        local alpha = tc[3]
        return ((colour / 0x10000) % 0x100) / 255., ((colour / 0x100) % 0x100) / 255., (colour % 0x100) / 255., alpha
    end

    function table.copy(t)
      local t2 = {}
      for k,v in pairs(t) do
       t2[k] = {v[1],v[2]}
      end
      return t2
    end

    function draw_corner(num,t)
        local shape=t[1]
        local radius=t[2]
        local x,y = t[3],t[4]
        if shape=="line" then
            if num == 1 then cairo_line_to(cr,radius,0) 
                elseif num == 2 then cairo_line_to(cr,x,radius) 
                elseif num == 3 then cairo_line_to(cr,x-radius,y)
                elseif num == 4 then cairo_line_to(cr,0,y-radius)
            end
        end
        if shape=="circle" then
		    local PI = math.pi
           if num == 1 then cairo_arc(cr,radius,radius,radius,-PI,-PI/2)
                elseif num == 2 then cairo_arc(cr,x-radius,y+radius,radius,-PI/2,0)
                elseif num == 3 then cairo_arc(cr,x-radius,y-radius,radius,0,PI/2) 
                elseif num == 4 then cairo_arc(cr,radius,y-radius,radius,PI/2,-PI)
            end
        end
        if shape=="curve" then
            if num == 1 then cairo_curve_to(cr,0,radius ,0,0 ,radius,0) 
                elseif num == 2 then cairo_curve_to(cr,x-radius,0, x,y, x,radius)
                elseif num == 3 then cairo_curve_to(cr,x,y-radius, x,y, x-radius,y)
                elseif num == 4 then cairo_curve_to(cr,radius,y, x,y, 0,y-radius)
            end
        end        
    end   

    --check values and set default values
    if t.x == nil then t.x = 0 end
    if t.y == nil then t.y = 0 end
    if t.w == nil then t.w = conky_window.width end
    if t.h == nil then t.h = conky_window.height end
    if t.radius == nil then t.radius = 0 end
    if t.border == nil then t.border = 0 end
    if t.colour==nil then t.colour={{1,0xFFFFFF,0.5}} end
    if t.linear_gradient ~= nil then 
        if #t.linear_gradient ~= 4 then
            t.linear_gradient = {t.x,t.y,t.width,t.height}
        end
    end 
    if t.angle==nil then t.angle = 0 end

	if t.skew_x == nil then t.skew_x=0  end
	if t.skew_y == nil then  t.skew_y=0 end
	if t.scale_x==nil then t.scale_x=1 end
	if t.scale_y==nil then t.scale_y=1 end	
	if t.rot_x == nil then t.rot_x=0  end
	if t.rot_y == nil then  t.rot_y=0 end
    
    if t.operator == nil then t.operator = "over" end
    if (t_operators[t.operator]) == nil then
        print ("wrong operator :",t.operator)
        t.operator = "over"
    end
    
    if t.radial_gradient ~= nil then 
        if #t.radial_gradient ~= 6 then
            t.radial_gradient = {t.x,t.y,0, t.x,t.y, t.width}
        end
    end 
    
    for i=1, #t.colour do    
        if #t.colour[i]~=3 then 
            print ("error in color table")
            t.colour[i]={1,0xFFFFFF,1} 
        end
    end

    if t.corners == nil then t.corners={ {"line",0} } end
    local t_corners = {}
    local t_corners = table.copy(t.corners)
    --don't use t_corners=t.corners otherwise t.corners is altered

    --complete the t_corners table if needed
    for i=#t_corners+1,4 do    
        t_corners[i]=t_corners[#t_corners]
        local flag=false
        for j,v in pairs(table_corners) do flag=flag or (t_corners[i][1]==v) end 
        if not flag then print ("error in corners table :",t_corners[i][1]);t_corners[i][1]="curve"  end
    end

    --this way :    
    --    t_corners[1][4]=x    
    --    t_corners[2][3]=y
    --doesn't work
    t_corners[1]={t_corners[1][1],t_corners[1][2],0,0}
    t_corners[2]={t_corners[2][1],t_corners[2][2],t.w,0}
    t_corners[3]={t_corners[3][1],t_corners[3][2],t.w,t.h}    
    t_corners[4]={t_corners[4][1],t_corners[4][2],0,t.h}        

    t.no_gradient = (t.linear_gradient == nil ) and (t.radial_gradient == nil )

    cairo_save(cr)
    cairo_translate(cr, t.x, t.y)
    if t.rot_x~=0 or t.rot_y~=0 or t.angle~=0 then
        cairo_translate(cr,t.rot_x,t.rot_y)
        cairo_rotate(cr,t.angle*math.pi/180)
        cairo_translate(cr,-t.rot_x,-t.rot_y)
    end
    if t.scale_x~=1 or t.scale_y~=1 or t.skew_x~=0 or t.skew_y~=0 then
	    local matrix0 = cairo_matrix_t:create()
	    tolua.takeownership(matrix0)
	    cairo_matrix_init (matrix0, t.scale_x,math.pi*t.skew_y/180	, math.pi*t.skew_x/180	,t.scale_y,0,0)
	    cairo_transform(cr,matrix0)    
    end
    
    local tc=t_corners
    cairo_move_to(cr,tc[1][2],0)
    cairo_line_to(cr,t.w-tc[2][2],0)
    draw_corner(2,tc[2])
    cairo_line_to(cr,t.w,t.h-tc[3][2])
    draw_corner(3,tc[3])
    cairo_line_to(cr,tc[4][2],t.h)
    draw_corner(4,tc[4])
    cairo_line_to(cr,0,tc[1][2])
    draw_corner(1,tc[1])
    
    if t.no_gradient then
        cairo_set_source_rgba(cr,rgba_to_r_g_b_a(t.colour[1]))
    else
        if t.linear_gradient ~= nil then
            pat = cairo_pattern_create_linear (t.linear_gradient[1],t.linear_gradient[2],t.linear_gradient[3],t.linear_gradient[4])
        elseif t.radial_gradient ~= nil then
            pat = cairo_pattern_create_radial (t.radial_gradient[1],t.radial_gradient[2],t.radial_gradient[3],
            	t.radial_gradient[4],t.radial_gradient[5],t.radial_gradient[6])
        end
        for i=1, #t.colour do
            cairo_pattern_add_color_stop_rgba (pat, t.colour[i][1], rgba_to_r_g_b_a(t.colour[i]))
        end
        cairo_set_source (cr, pat)
        cairo_pattern_destroy(pat)
    end 
     
    cairo_set_operator(cr,t_operators[t.operator]) 

    if t.border>0 then
        cairo_close_path(cr)
        if t.dash ~= nil then cairo_set_dash(cr, t.dash, 1, 0.0) end
        cairo_set_line_width(cr,t.border)
        cairo_stroke(cr)
    else
        cairo_fill(cr)
    end

    cairo_restore(cr)
end
