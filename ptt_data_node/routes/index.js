
/*
 * GET home page.
 */

var mongodb = require('mongodb');
var async = require('async');
var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
var db = new mongodb.Db('Gossiping', mongodbServer);


exports.index = function(req, res){
	//var fs = require('fs');
	//fs.readFile('./data/groupData.json', function (err, data) {
	//	if (err) throw err;
	//	console.log(data);
	//	res.render('index', { title: 'Express' , json: data});
	//});

    var dateObj = new Date()
    var timeStemp = dateObj.getTime()
    timeStemp -= 1000 * 60*60*24*5;

	db.open(function() {
		async.parallel({
    			single: function(callback1){
					db.collection('single', function(err, collection) {
						async.parallel({
    						s_all: function(callback){
        						collection.find({'time':{"$gte":(timeStemp/1000)}}, {limit:10, fields:{'_id': 0}})
					  						.sort({'push.all': -1})
					  						.toArray(function(err, docs) {
            									callback(err, docs);
        									});
    						},
    						s_g: function(callback){
        						collection.find({'time':{"$gte":(timeStemp/1000)}}, {limit:10, fields:{'_id': 0}})
					  						.sort({'push.g': -1})
					  						.toArray(function(err, docs) {
            									callback(err, docs);
        									});
    						},
    						s_b: function(callback){
        						collection.find({'time':{"$gte":(timeStemp/1000)}}, {limit:10, fields:{'_id': 0}})
					  						.sort({'push.b': -1})
					  						.toArray(function(err, docs) {
            									callback(err, docs);
        									});
    						}
						},
						function(err, results) {
    						callback1(err, results)
						});
					});
				},
				group: function(callback1){
					db.collection('group', function(err, collection) {
						async.parallel({
    						g_all: function(callback){
        						collection.find({'time':{"$gte":(timeStemp/1000)}}, {limit:10, fields:{'_id': 0}})
								  .sort({'push.all': -1})
								  .toArray(function(err, docs) {
            						callback(err, docs);
        						});
    						},
						},
						function(err, results) {
    						callback1(err, results)
						});

					});
				},
			},
			function(err, results) {
    			res.render('index', { title: 'Express' , s_all: results['single']['s_all'], s_g: results['single']['s_g'], s_b: results['single']['s_b'], g_all: results['group']['g_all']});
    			db.close();

			});
	});
  	
};