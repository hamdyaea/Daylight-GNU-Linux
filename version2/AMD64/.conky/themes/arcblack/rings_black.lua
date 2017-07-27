--[[ RINGS with SECTORS widget
	v1.1 by wlourf (07 Jan. 2011)
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
	--line1

--[[{
	name="",
	arg="",
	max=256,
	xc=85,
	yc=100,
	thickness=65,
	radius=70,
	sectors=1,
	gap_sectors=0,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,0.},{0.5,0x000000,.5},{1,0x000000,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},
]]

{
	name="cpu",
	arg="cpu2",
	max=100,
	xc=85,
	yc=100,
	thickness=15,
	radius=40,
	sectors=10,
	gap_sectors=0,
	border_size=0,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x585858,1.},{1,0x000000,01.}},
	fg_colour1={{0,0x303030,1.},{1,0x020202,01.}},
	fg_colour2={{0,0xC00000,1.},{01,0x400000,01.0}},
	bd_colour1={{0,0xFFFFFF,1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,1}},
	},

{
	name="cpu",
	arg="cpu1",
	max=100,
	xc=85,
	yc=100,
	thickness=15,
	radius=25,
	sectors=10,
	gap_sectors=0,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.1,0x000000,1.},{1,0x585858,1.}},
	fg_colour1={{0.1,0x020202,01.},{1,0x303030,1.}},
	fg_colour2={{0.1,0x400000,01.},{1,0xC00000,1.}},
	},

{
	name="hwmon",
	arg="0 temp 1",
	max=100,
	xc=85,
	yc=100,
	thickness=7,
	radius=48,
	sectors=10,
	gap_sectors=0,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,01.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},

{
	name="memperc",
	arg="",
	max=100,
	xc=85,
	yc=100,
	thickness=10,
	radius=60,
	sectors=10,
	gap_sectors=0,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},

--[[{--ombre top cpu
	name="",
	arg="",
	max=256,
	xc=32,
	yc=195,
	thickness=20,
	radius=20,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,1.0},{0.5,0x000000,.5},{1,0x000000,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},

{--arc top cpu
	name="",
	arg="",
	max=256,
	xc=32,
	yc=195,
	thickness=15,
	radius=15,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x808080,.4},{0.5,0x808080,.2},{1,0x808080,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},
{--ombre top mem
	name="",
	arg="",
	max=256,
	xc=32,
	yc=231,
	thickness=20,
	radius=20,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,1.0},{0.5,0x000000,.5},{1,0x000000,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},

{--arc top mem
	name="",
	arg="",
	max=256,
	xc=32,
	yc=231,
	thickness=15,
	radius=15,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0xFFE807,1.0},{0.5,0xFFE807,.5},{1,0xFFE807,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},


{
	name="",
	arg="",
	max=256,
	xc=85,
	yc=500,
	thickness=50,
	radius=50,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,0.},{0.5,0x000000,.5},{1,0x000000,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},
]]
{
	name="fs_used_perc",
	arg="/home",
	max=100,
	xc=85,
	yc=500,
	thickness=25,
	radius=32,
	sectors=10,
	gap_sectors=0,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},
{
	name="execp",
	arg="hddtemp -n /dev/sda",
	max=100,
	xc=85,
	yc=500,
	thickness=10,
	radius=42,
	sectors=10,
	gap_sectors=0,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},
--[[
{
	name="",
	arg="",
	max=256,
	xc=85,
	yc=600,
	thickness=50,
	radius=50,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,0.},{0.5,0x000000,.5},{1,0x000000,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},
]]
{
	name="fs_used_perc",
	arg="/media/Data",
	max=100,
	xc=85,
	yc=600,
	thickness=25,
	radius=32,
	sectors=10,
	gap_sectors=0,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},
{
	name="execp",
	arg="hddtemp -n /dev/sdb",
	max=100,
	xc=85,
	yc=600,
	thickness=10,
	radius=42,
	sectors=10,
	gap_sectors=0,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},
--[[
{
	name="",
	arg="",
	max=256,
	xc=85,
	yc=325,
	thickness=65,
	radius=70,
	sectors=1,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,0.},{0.5,0x000000,.5},{1,0x000000,0.}},
	fg_colour1={{0,0xFFFF00,0.1},{0.5,0xFFFF00,1.0},{1,0xFFFF00,0.1}},
	fg_colour2={{0.,0xFF1647,0.1},{0.5,0xFF1647,1.0},{1,0xFF1647,0.1}},
	},
]]
	{
	name="upspeedf",
	arg="wlan0",
	max=256,
	xc=85,
	yc=325,
	thickness=26,
	radius=40,
	sectors=5,
	gap_sectors=0,
	fill_sector=false,
	start_angle=270,
	end_angle=360,
	inverse_arc=false,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},
{
	name="downspeedf",
	arg="wlan0",
	max=2100,
	xc=85,
	yc=325,
	thickness=26,
	radius=40,
	sectors=5,
	gap_sectors=0,
	fill_sector=false,
	start_angle=270,
	end_angle=180,
	inverse_arc=true,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},
{
	name="wireless_link_qual_perc",
	arg="wlan0",
	max=100,
	xc=85,
	yc=325,
	thickness=10,
	radius=60,
	sectors=10,
	gap_sectors=0,
	fill_sector=false,
	start_angle=180,
	end_angle=360,
	bg_colour1={{0.,0x000000,01.},{0.5,0x585858,1},{1,0x000000,1.}},
	fg_colour1={{0,0x020202,01.},{0.5,0x303030,1},{1,0x020202,01.}},
	fg_colour2={{0,0x400000,01.},{0.5,0xC00000,1.},{1,0x400000,01.}},
	},


	
}
--END OF PARAMETERS HERE

--main function

	--if conky_window==nil then return end

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
