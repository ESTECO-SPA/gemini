## QUICK START
### Run a scenario based on the encoded VISCANDO's IRL model
The source code of IRL architecture and IRL model developed during this project is not available on this repository.
You can download an Linux executable which encode the original model [here](https://drive.google.com/file/d/1F8vK_qmj0Rz_4y3kK31fwp8YRm364Ldv/view?usp=sharing) 
it has been created using [pyInstaller](https://pyinstaller.org/en/stable/). Please considet that it is not performing properly mainly because there is a delay in stdin, stdout conversion (see `external.IRL.Auxiliary_functions.architectures_interface.VariationalGeneratorEncoded`) 

Follows these steps: 
- extract this zip file in the DATA_PATH folder.
- run `contribution/irl_model_encoded.py`
