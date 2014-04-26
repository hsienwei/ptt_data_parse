
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
            			res.render('rank', { rank: docs[0], board_id:req.params.id });
    					db.close();
        			   });
		});
	});

};


exports.rank_single = function(req, res){
	if (req.params.sort_type == null)
		res.redirect('/rank/' + req.params.id + '/single/g/10');
	else	
		res.redirect('/rank/' + req.params.id + '/single/' + req.params.sort_type + '/10');
};

exports.rank_single_num = function(req, res){
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.params.id, mongodbServer);
	db.open(function() {
		rangeDay = Date.now()/1000 - 60 * 60 * 24 * 5 
		db.collection('single', function(err, collection) {
			var cursor = collection.find({'time':{"$gte":rangeDay}}, {limit:req.params.num, fields:{}})
			var sort_cursor;
			if(req.params.sort_type == 'g')		
				sort_cursor = cursor.sort({ 'push.g': -1})
			else if(req.params.sort_type == 'b')		
				sort_cursor = cursor.sort({ 'push.b': -1})	  
			else 
				sort_cursor = cursor.sort({ 'push.all': -1})

			sort_cursor.toArray(function(err, docs) {
            	res.render('rank_single', { rank: docs});
    			db.close();
        	});
		});
	});
};

exports.rank_group = function(req, res){
	console.log(req.params.sort_type);
	if (req.params.sort_type == null)
		res.redirect('/rank/' + req.params.id + '/group/g/10');
	else	
		res.redirect('/rank/' + req.params.id + '/group/' + req.params.sort_type + '/10');
};

exports.rank_group_num = function(req, res){
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.params.id, mongodbServer);
	db.open(function() {
		rangeDay = Date.now()/1000 - 60 * 60 * 24 * 5 
		db.collection('group', function(err, collection) {
			
			var cursor = collection.find({'time':{"$gte":rangeDay}}, {limit:req.params.num, fields:{}})
			var sort_cursor;
			if(req.params.sort_type == 'g')		
				sort_cursor = cursor.sort({ 'push.g': -1})
			else if(req.params.sort_type == 'b')		
				sort_cursor = cursor.sort({ 'push.b': -1})	  
			else 
				sort_cursor = cursor.sort({ 'push.all': -1})
			sort_cursor.toArray(function(err, docs) {
            	res.render('rank_group', { rank: docs, board_id:req.params.id});
    			db.close();
        	});
		});
	});
};


exports.grouplist = function(req, res){
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.params.id, mongodbServer);
	db.open(function() {
		db.collection('group', function(err, collection) {
			var ObjectID = mongodb.ObjectID;
			collection.findOne({_id:new ObjectID(req.params.title)}, function(err, col) {
					  		console.log(req.params.id);
							console.log(col);


					  		if(err)
					  		{
					  			db.close();
					  			res.send('error');
					  		}
					  		else
					  		{
					  			console.log(col['groupList']);
								db.collection('single', function(err, collection) {
					  				collection.find({"id":{"$in":col['groupList']}}, { fields:{}})
					  				.sort({'time': 1})
					  				.toArray(function(err, docs) {
					  					if(err)
					  						res.send('error');
					  					else
					  						console.log(docs);
					  						res.render('grouplist', { list: docs});
					  					db.close();

					  				});
					  			});
					  		}
            				
        			   });
		});
	});
};