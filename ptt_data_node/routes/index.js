
/*
 * GET home page.
 */

exports.index = function(req, res){
	var fs = require('fs');
	fs.readFile('./data/groupData.json', function (err, data) {
		if (err) throw err;
		console.log(data);
		res.render('index', { title: 'Express' , json: data});
	});

  
};