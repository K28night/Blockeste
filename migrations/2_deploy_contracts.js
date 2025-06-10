const PDFStorage = artifacts.require("PDFStorage");

module.exports = function (deployer) {
  deployer.deploy(PDFStorage);
};
