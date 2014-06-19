
/**
 * Module dependencies.
 */

var express = require('express');
var partials = require('express-partials');
var routes = require('./routes');
var user = require('./routes/user');
var http = require('http');
var path = require('path');


var app = express();

// all environments
app.set('port', process.env.PORT || 80);
app.set('views', path.join(__dirname, 'views'));
app.set('view engine', 'ejs');
app.use(partials());
app.use(express.favicon());
app.use(express.logger('dev'));
app.use(express.json());
app.use(express.urlencoded());
app.use(express.methodOverride());
app.use(app.router);
app.use(express.static(path.join(__dirname, 'public')));

// development only
if ('development' == app.get('env')) {
  app.use(express.errorHandler());
}

//app.get('/', routes.index);
app.get('/', function (req, res) {
    console.log("get /");
    res.sendfile(__dirname + '/public/index.html');
});

app.get('/rank/:id', routes.rank);
app.get('/rank/:id/single', routes.rank_single);
// app.get('/rank/:id/single/:sort_type', routes.rank_single);
//app.get('/rank/:id/single/:sort_type/:num', routes.rank_single_num);
app.get('/rank/:id/group', routes.rank_group);
// app.get('/rank/:id/group/:sort_type', routes.rank_group);
// app.get('/rank/:id/group/:sort_type/:num', routes.rank_group_num);
app.get('/grouplist/:id/:title', routes.grouplist);

app.get('/board_select/:act', routes.board_select);

app.post('/singleRankGet', routes.singleRankGet)
app.post('/groupRankGet', routes.groupRankGet)

app.get('/links/:id', routes.links);
//app.get('/users', user.list);

app.get('/keyword/:id', routes.keyword);
app.get('/test', function (req, res) {
    console.log("get /");
    res.sendfile(__dirname + '/public/simple.html');
});

http.createServer(app).listen(app.get('port'), function(){
  console.log('Express server listening on port ' + app.get('port'));
});
