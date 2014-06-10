
/*
 * GET home page.
 */

var mongodb = require('mongodb');
var async = require('async');


// exports.index = function(req, res){
// 	//res.render('./index.html');
//    	res.sendfile(__dirname + '/public/index.html');
// };

exports.board_select = function(req, res){
	var action = req.params.act;
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db('setting', mongodbServer);
	db.open(function() {
		db.collection('board_list', function(err, collection) {
			collection.find({}, {fields:{'_id': 0}})
					  .toArray(function(err, docs) {
					  	console.log(docs);
            			 res.render('board_select', { 'act': action , 'data':docs});
    					db.close();
        			   });
		});
	});
};


exports.rank = function(req, res){
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.params.id, mongodbServer);
	db.open(function() {
		db.collection('rank', function(err, collection) {
			collection.find({}, {limit:1, fields:{'_id': 0}})
					  .sort({'time': -1})
					  .toArray(function(err, docs) {
					  	//console.log(docs);
            			res.render('rank', { rank: docs[0], board_id:req.params.id });
    					db.close();
        			   });
		});
	});

};


exports.rank_single = function(req, res){
	var sortType = req.params.sort_type;
	if(sortType == null)    req.params.sort_type = 'g';

	res.render('rank_single', { board:req.params.id, sort:sortType});
};

// exports.rank_group = function(req, res){
// 	console.log(req.params.sort_type);
// 	if (req.params.sort_type == null)
// 		res.redirect('/rank/' + req.params.id + '/group/g/10');
// 	else	
// 		res.redirect('/rank/' + req.params.id + '/group/' + req.params.sort_type + '/10');
// };

exports.rank_group = function(req, res){

	var sortType = req.params.sort_type;
	if(sortType == null)    req.params.sort_type = 'g';

	res.render('rank_group', { board:req.params.id, sort:sortType});

	// console.log('a');

	// var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	// var db = new mongodb.Db(req.params.id, mongodbServer);
	// db.open(function() {
	// 	console.log('b');
	// 	rangeDay = Date.now()/1000 - 60 * 60 * 24 * 5 
	// 	db.collection('group', function(err, collection) {
	// 		console.log('c');
	// 		var cursor = collection.find({'time':{"$gte":rangeDay}}, {limit:100, fields:{}})
	// 		var sort_cursor;
	// 		// if(req.params.sort_type == 'g')		
	// 		// 	sort_cursor = cursor.sort({ 'extra_push_point.g': -1})
	// 		// else if(req.params.sort_type == 'b')		
	// 		// 	sort_cursor = cursor.sort({ 'extra_push_point.b': -1})	  
	// 		// else 
	// 		// 	sort_cursor = cursor.sort({ 'extra_push_point.all': -1})
	// 		sort_cursor = cursor.sort({ 'score': -1})
	// 		sort_cursor.toArray(function(err, docs) {
	// 			console.log('d');
 //            	res.render('rank_group', { rank: docs, board_id:req.params.id});
 //    			db.close();
 //        	});
	// 	});
	// });
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


exports.links = function(req, res){
	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.params.id, mongodbServer);
	db.open(function() {
		db.collection('single', function(err, collection) {
			collection.find({links:{ $exists: true}}, {limit:1000, fields:{'_id': 0}})
					  .sort({'time': -1})
					  .toArray(function(err, docs) {
					  		var ary = [];
					  		for(var i = 0; i < docs.length; ++i)
					  		{
					  			if(docs[i]['links'] != null)
					  			{
					  				for(var j = 0; j < docs[i]['links'].length; ++j)
					  				{
					  					ary.push(docs[i]['links'][j]);
					  				}
					  			}
					  		}
					  		var data = link_process(ary);
							res.render('links', { list: ary, data:data});
							db.close();
						});
		});
	});
};

function link_process(data)
{
	var result = []

	for(var idx in  data)
	{	
		var obj = data[idx];
		console.log(obj);
		var isFind = false;
		for(var r_idx in result)
		{
			var r_obj = result[r_idx];
			if(r_obj['real'] == obj['real'])
			{
				isFind = true;
			}
		}
		if(!isFind)
			result.push(obj);
	}

	console.log(result);
	var a = ['nownews.com',
			 'wikimedia.org',
			 'wikipedia.org',
			 'facebook.com',
			 'appledaily.com.tw',
			 'chinatimes.com',
			 'ettoday.net',
			 'youtube.com',
			 'imgur.com',
			 'news.yahoo.com',
			 'yam.com',
			 'ltn.com.tw',
			 'peoplenews.tw',
			 'udn.com',
			 'peopo.org',
			 'cw.com.tw',
			 'newtalk.tw',
			 'tvbs.com.tw',
			 'ppt.cc',
			 'cts.com.tw',
			 'ttv.com.tw',
			 'cna.com.tw',
			 'ntdtv.com',
			 'nextmag.com.tw',
			 'hk.apple.nextmedia.com',
			 'bbc.co.uk',
			 'rti.org.tw',
			 'epochtimes.com'];

	var b = ['nownews.com',
			 '維基百科',
			 '維基百科',
			 'facebook.com',
			 '蘋果日報',
			 '中時電子報',
			 '東森新聞雲',
			 'youtube',
			 'imgur',
			 'Yahoo奇摩新聞',
			 'yam蕃薯藤新聞',
			 '自由時報',
			 '民報',
			 '聯合新聞網',
			 '公民新聞',
			 '天下雜誌',
			 '新頭殼',
			 'TVBS',
			 'ppt.cc',
			 '華視',
			 '台視',
			 '中央社',
			 '新唐人電視台',
			 '壹週刊',
			 '蘋果日報(香港)',
			 'BBC中文網(簡體)',
			 '中央廣播電台',
			 '大紀元'];	

	var c = [1,	//news
			 2,
			 2,	//social
			 2, 
			 1,
			 1,
			 1,
			 2,
			 2,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 2,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1,
			 1];		 

	var ary = {};

	for(var i=0; i< result.length; ++i)
	{
		var link = result[i]['real'];
		var isFind = false;
		for(var j=0; j< a.length; ++j)
		{
			
			if(link.search(a[j]) != -1)
			{
				if(b[j] in ary)
				{
					ary[b[j]]['count'] += 1;
				}
				else
				{
					ary[b[j]] = {}
					ary[b[j]]['kind'] = c[j];
					ary[b[j]]['count'] = 1;
					ary[b[j]]['data'] = [];
				}
				ary[b[j]]['data'].push(link);
				isFind = true;
			}
		}
		if(!isFind)
		{
			if('其他' in ary)
			{
				
				ary['其他']['count'] += 1;
			}
			else
			{
				ary['其他'] = {}
				ary['其他']['kind'] = 0;
				ary['其他']['count'] = 1;
				ary['其他']['data'] = [];
			}
			ary['其他']['data'].push(link);
		}
	}
	console.log(ary);
	return ary;
}

exports.singleRankGet = function(req, res)
{
	console.log(req.body.pageIdx);
	console.log(req.body.board);
	console.log(req.body.sort);

	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.body.board, mongodbServer);
	db.open(function() {
		rangeDay = Date.now()/1000 - 60 * 60 * 24 * 5 
		db.collection('single', function(err, collection) {
			var cursor = collection.find({'time':{"$gte":rangeDay}}, {skip: (req.body.pageIdx * 10), limit:10, fields:{}})
			var sort_cursor;
			// if(req.body.sort == 'g')		
			// 	sort_cursor = cursor.sort({ 'extra_push_point.g': -1})
			// else if(req.body.sort == 'b')		
			// 	sort_cursor = cursor.sort({ 'extra_push_point.b': -1})	  
			// else 
			// 	sort_cursor = cursor.sort({ 'extra_push_point.all': -1})
			sort_cursor = cursor.sort({ 'score': -1})
			sort_cursor.toArray(function(err, docs) {
            	res.send(docs);
    			db.close();
        	});
		});
	});

}

exports.groupRankGet = function(req, res)
{
	console.log(req.body.pageIdx);
	console.log(req.body.board);
	console.log(req.body.sort);

	var mongodbServer = new mongodb.Server('localhost', 27017, { auto_reconnect: true, poolSize: 10 });
	var db = new mongodb.Db(req.body.board, mongodbServer);
	db.open(function() {
		rangeDay = Date.now()/1000 - 60 * 60 * 24 * 5 
		db.collection('group', function(err, collection) {
			var cursor = collection.find({'time':{"$gte":rangeDay}}, {skip: (req.body.pageIdx * 10), limit:10, fields:{}})
			var sort_cursor;
			// if(req.body.sort == 'g')		
			// 	sort_cursor = cursor.sort({ 'extra_push_point.g': -1})
			// else if(req.body.sort == 'b')		
			// 	sort_cursor = cursor.sort({ 'extra_push_point.b': -1})	  
			// else 
			// 	sort_cursor = cursor.sort({ 'extra_push_point.all': -1})
			sort_cursor = cursor.sort({ 'score': -1})
			sort_cursor.toArray(function(err, docs) {
				console.log(docs);
            	res.send(docs);
    			db.close();
        	});
		});
	});

}