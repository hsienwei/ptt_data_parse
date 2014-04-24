
/*
 * GET home page.
 */

var mongodb = require('mongodb');
var async = require('async');




exports.index = function(req, res){
	res.render('index');
   	
};


exports.rank = function(req, res){
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.params.id, mongodbServer);
	db.open(function() {
		db.collection('rank', function(err, collection) {
			collection.find({}, {limit:1, fields:{'_id': 0}})
					  .sort({'time': -1})
					  .toArray(function(err, docs) {
					  	console.log(docs);
            			res.render('rank', { rank: docs[0]});
    					db.close();
        			   });
		});
	});

};