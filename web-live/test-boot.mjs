// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// SPDX-License-Identifier: GPL-3.0-only
// Execute the real Linux guest using the same emulator as the browser.
import fs from 'node:fs';
import path from 'node:path';
import {V86} from '../dist/web-live-build/emulator/package/build/libv86.mjs';
const dir=path.resolve('dist/web-live');
let log='', finished=false;
const started=Date.now();
const emulator=new V86({
 wasm_path:dir+'/v86.wasm',
 bios:{url:dir+'/seabios.bin'},
 vga_bios:{url:dir+'/vgabios.bin'},
 bzimage:{url:dir+'/vmlinuz.bin'},
 initrd:{url:dir+'/initrd.bin'},
 cmdline:'rdinit=/init console=ttyS0,115200 console=tty0 loglevel=4 random.trust_cpu=on pci=conf1 tsc=reliable',
 memory_size:Number(process.env.DAYLIGHT_TEST_MEMORY_MIB || 256)*1024*1024,
 vga_memory_size:8*1024*1024,
 acpi:false,
 autostart:true,
 disable_speaker:true
});
const timer=setTimeout(()=>finish(false,'Guest boot deadline reached'),180000);
function finish(success,message){
 if(finished)return;finished=true;clearTimeout(timer);
 fs.writeFileSync(dir+'/boot-test.log',log);
 console.log(message, 'elapsed_ms', Date.now()-started);
 emulator.destroy();process.exit(success?0:1);
}
emulator.add_listener('serial0-output-byte',byte=>{
 const char=String.fromCharCode(byte);log+=char;process.stdout.write(char);
 if(log.includes('DAYLIGHT_WEB_GRAPHICS_FAILED'))finish(false,'Graphics startup failed');
 if(log.includes('DAYLIGHT_WEB_DESKTOP_READY'))finish(true,'Real Alpine/Fluxbox guest reached its desktop');
});
process.on('uncaughtException',error=>finish(false,error.stack));
