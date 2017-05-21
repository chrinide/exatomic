// Entry point for the notebook bundle containing custom model definitions.
//
// Setup notebook base URL
//
// Some static assets may be required by the custom widget javascript. The base
// url for the notebook is not known at build time and is therefore computed
// dynamically.
var _ = require("underscore");
var __webpack_public_path__ = document.querySelector("body").getAttribute("data-base-url") + "nbextensions/jupyter-exa/";
// Export widget models and views, and the npm package version number.
module.exports = _.extend(
    {},
    require("./test.js")
//    require("./example.js"), 
//    require("./example2.js"),
//    require("./foo/base.js"), 
//    require("./exa-three.js"),
//    require("./app.js"),
//    require("./functions.js"),
//    require("./universe.js"),
//    require("./test.js")
);
module.exports["version"] = require("../package.json").version;
