set /p ext="Enter file extension: "



"D:\OneDrive\Documents\Graduate School\PSCP.exe"  -r -l tarch -P 22 -pw =-09][po=-09 ../*%ext% ssh.fsl.byu.edu:/fslhome/tarch/compute/673/wordrnn/

"D:\OneDrive\Documents\Graduate School\PSCP.exe"  -r -l tarch -P 22 -pw =-09][po=-09 ../processing/*%ext% ssh.fsl.byu.edu:/fslhome/tarch/compute/673/wordrnn/processing/

"D:\OneDrive\Documents\Graduate School\PSCP.exe"  -r -l tarch -P 22 -pw =-09][po=-09 ../data/*%ext% ssh.fsl.byu.edu:/fslhome/tarch/compute/673/wordrnn/data/


pause
