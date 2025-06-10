const Migrations = artifacts.require("forensic");

module.exports = function(deployer) {
  deployer.deploy(Migrations);
};
