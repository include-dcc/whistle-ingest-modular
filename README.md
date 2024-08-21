# Whistle Ingest Modular
This repository is intended as the first step toward a fully automated whistle ingest for INCLUDE. The input for this project is harmonized data or study/dataset content. The output is FHIR resources which can be loaded into a FHIR server.

This project is different from whistle-ingest-linkml in that the project will, eventually, allow the same configurations to be used to ETL Study or Dataset or Harmonized Data based on the run arguments. We will also be supporting projection versioning once the pipeline used supports it. 

# Study Configuration Details
For the time being, you will need to specify which projection library using the *project_lib* parameter. The plan will be for each type of projection configuration will be nested as a subdirectory inside projector. Inside will be "current" or a particular version. By default, I'm assuming we'll use "current", however, if we have released data and then make changes to the FHIR mapping approach, we'll copy the contents of current to a version number and proceed with changes inside the current directory. 

Ultimately, we will probably want to actually make formal releases and then check the projections out using git hub releases. However, that will require running within a VM and building the VM for each run. 

# Study.enrollment
If a study has participant data, the enrollment will be populated with the study group. However, if we don't have that information, the enrollment property will be missing from the study resource. 