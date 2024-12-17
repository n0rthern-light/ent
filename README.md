# ent.py
BMP Entropy image generator from a file

### Usage
`ent.py <input-file>`
The entropy image will be generated as `<input-file>.bmp`

### Example entropy image
![ent_example](https://github.com/user-attachments/assets/1dfefdc7-0741-4fb6-81d5-cc236a2199d5)

### Print spikes
Pass `--spikes` option to enable entropy spike detection based on standard deviation 
```zsh
$ ent.py i_am_quite_large.bin --spikes                  [15:19:54]
0x12000 (size: 0x400): Entropy spike from 2.85 to 3.70
0x12400 (size: 0x400): Entropy spike from 3.70 to 6.06
0x555000 (size: 0x400): Entropy spike from 2.85 to 4.14
0x555400 (size: 0x400): Entropy spike from 4.14 to 5.56
0x7ac000 (size: 0x400): Entropy spike from 2.86 to 4.76
0x7ac400 (size: 0x400): Entropy spike from 4.76 to 3.99
```
