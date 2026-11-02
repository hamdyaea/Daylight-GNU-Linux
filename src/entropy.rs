// Developer: Hamdy Abou El Anein
// Contact: info@daylightlinux.ch
// Copyright (C) 2026 Hamdy Abou El Anein
// SPDX-License-Identifier: GPL-3.0-only
//! Linux getrandom with initialization blocking and unbiased rejection sampling.
use std::{ffi::c_void, io};
extern "C" {
    fn getrandom(buf: *mut c_void, buflen: usize, flags: u32) -> isize;
}
pub fn fill(buf: &mut [u8]) -> io::Result<()> {
    let mut offset = 0;
    while offset < buf.len() {
        let chunk = (buf.len() - offset).min(256);
        // SAFETY: a valid exclusive slice is passed for its remaining length.
        // flags=0 waits for kernel CSPRNG initialization; no fallback RNG.
        let n = unsafe { getrandom(buf[offset..].as_mut_ptr().cast(), chunk, 0) };
        if n < 0 {
            let e = io::Error::last_os_error();
            if e.kind() == io::ErrorKind::Interrupted {
                continue;
            }
            return Err(e);
        }
        if n == 0 {
            return Err(io::Error::new(
                io::ErrorKind::UnexpectedEof,
                "getrandom returned zero",
            ));
        }
        offset += n as usize;
    }
    Ok(())
}
pub fn uniform(upper: u32) -> io::Result<u32> {
    if upper == 0 {
        return Err(io::Error::new(
            io::ErrorKind::InvalidInput,
            "empty random range",
        ));
    }
    let threshold = upper.wrapping_neg() % upper;
    loop {
        let mut b = [0; 4];
        fill(&mut b)?;
        let n = u32::from_ne_bytes(b);
        if n >= threshold {
            return Ok(n % upper);
        }
    }
}
#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn rejects_zero() {
        assert!(uniform(0).is_err());
    }
    #[test]
    fn bounds() {
        for _ in 0..200 {
            assert!(uniform(6).unwrap() < 6);
        }
    }
    #[test]
    fn single_choice() {
        assert_eq!(uniform(1).unwrap(), 0);
    }
    #[test]
    fn fills_and_empty() {
        let mut b = [0; 600];
        fill(&mut b).unwrap();
        assert!(b.iter().any(|x| *x != 0));
        fill(&mut []).unwrap();
    }
}
