
package.path = "/home/jacques/.conky/arcblack/?.lua" --chemin a adapter 
require 'rings_black' --for scriptA.lua ".lua" is not required here
require 'bar_black'

function conky_main()
     conky_main_bars()
     conky_main_rings()
end
