<?php
if (isset($_POST['content'])) {
    file_put_contents("./fs/input", $_POST['content']);
    $cmd = escapeshellcmd("./demo.py");
    shell_exec($cmd);
    $keywordRank = explode(',', file_get_contents("./fs/output"));
    foreach($keywordRank as $i => $keyword) {
        $replace[$i] = "<span style=\"color:red;\">" . $keyword . "</span>";
    }
}
?>
<!DOCTYPE html>
<html lang="zh-Hant-TW">
<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta name="description" content="">
    <meta name="author" content="">
    <link href="media/bootstrap.min.css" rel="stylesheet">
    <link href="media/bootstrap-theme.css" rel="stylesheet">
    <title>Radio Keyword</title>
    <style>
        body {
            padding-top: 70px;
        }

        .hero-spacer {
            margin-top: 50px;
        }

        .hero-feature {
            margin-bottom: 30px;
        }

        footer {
            margin: 50px 0;
        }
        .chart div {
          font: 10px sans-serif;
          background-color: steelblue;
          text-align: right;
          padding: 3px;
          margin: 1px;
          color: white;
        }
        .form-group {
        	width: 100%;
        }
        th {
            cursor: pointer;

        }
        .sortorder:after {
          content: '\25b2';   // BLACK UP-POINTING TRIANGLE
        }
        .sortorder.reverse:after {
          content: '\25bc';   // BLACK DOWN-POINTING TRIANGLE
        }
    </style>
</head>

<body ng-app="myApp" ng-controller="libController">
    <nav class="navbar navbar-inverse navbar-fixed-top" role="navigation">
        <div class="container">
            <div class="navbar-header">
                <button type="button" class="navbar-toggle" data-toggle="collapse" data-target="#bs-example-navbar-collapse-1">
                    <span class="sr-only">Toggle navigation</span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                    <span class="icon-bar"></span>
                </button>
                <a class="navbar-brand" href="#">Radio Keyword</a>
            </div>
            <div class="collapse navbar-collapse" id="bs-example-navbar-collapse-1">
<!--                 <ul class="nav navbar-nav">
                    <li>
                        <a href="#">Home</a>
                    </li>
                </ul> -->
            </div>
        </div>
    </nav>

    <div class="container">
        <header class="jumbotron hero-spacer">
            <h1>Radio Keyword</h1>

            <p>
            <form method="post" style="margin-top:50px;">
            	<div class="form-group">
                    <input type="text" class="form-control" name="content">
				</div>
			</p>
            <p style="margin-top:30px;">
                <input type="submit" 
                value="擷取關鍵字" class="btn btn-primary btn-large btn-block" />
            </p>
            </form>
        </header>

        <hr>


        <div id="showData">

            <div>
            <?php if(isset($keywordRank)):?>
                <?php foreach($keywordRank as $i => $keyword): ?>
                   <h2> <?=$i+1?>. <?=$keyword?></h2></br>
                <?php endforeach?>
            <?php endif?>
            </div>
        </div>
        <footer>
            <div class="row">
                <div class="col-lg-12">
                    <p>Copyright &copy; WIRL 2016</p>
                </div>
            </div>
        </footer>

    </div>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/1.12.4/jquery.min.js"></script>
<script src="media/bootstrap.min.js"></script>
<script src="https://d3js.org/d3.v3.min.js" charset="utf-8"></script>
<script src="http://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.min.js"></script>
</script>
</body>
</html>