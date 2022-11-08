{ lib, buildPythonPackage, python, pytestCheckHook, doit, poetry
, pytest-regressions }:

buildPythonPackage {
  pname = "doit-ext";
  version = "0.1";
  format = "pyproject";

  src = ./.;

  nativeBuildInputs = [ poetry ];
  propagatedBuildInputs = [ doit ];

  # The cythonized extensions are required to exist in the pygeos/ directory
  # for the package to function. Therefore override of buildPhase was
  # necessary.
  # buildPhase = ''
  #   ${python.interpreter} setup.py build_ext --inplace
  #   ${python.interpreter} setup.py bdist_wheel
  # '';

  checkInputs = [ pytestCheckHook pytest-regressions ];

  pythonImportsCheck = [ "doit_ext" ];

  meta = with lib; {
    description = "doit-ext";
    homepage = "https://github.com/nialov/doit-ext";
    license = licenses.mit;
    maintainers = with maintainers; [ nialov ];
  };
}
