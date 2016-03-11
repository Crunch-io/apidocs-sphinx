## Projects

Projects are ....

They live under /projects/ and will list the projects that the logged user
is a member or owner of.

### Catalog

The projects catalog will list all the projects the logged user is a member of.
Here you can create new projects via POST

#### GET

```http
GET /projects/ HTTP/1.1
```

```json
{
  "element": "shoji:catalog",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/",
  "index": {
    "http:\/\/local.crunch.io:8080\/api\/projects\/4643\/": {
      "name": "Project 1",
      "id": "4643",
      "icon": ""
    },
    "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/": {
      "name": "Project 2",
      "id": "6c01",
      "icon": ""
    }
  }
}
```

#### POST

New projects need a name (no uniqueness enforced) and will belong to the logged
user, making it its initial member.

```http
POST /projects/ HTTP/1.1
```

Payload example:

```json
{
    "body": {
        "name": "My new project"
    }
}
```

### Entity

#### GET

```http
GET /projects/abcd/ HTTP/1.1
```

```json
{
  "element": "shoji:entity",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/",
  "catalogs": {
    "datasets": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/datasets\/",
    "members": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/members\/"
  },
  "views": {
    "icon": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/icon\/"
  },
  "body": {
    "name": "Project 2",
    "description": "Long description text",
    "icon": "",
    "id": "",
  }
}
```

#### DELETE

Deleting a project will *NOT* delete its datasets. It will change their 
ownership to the logged user.

```http
DELETE /projects/abcd/ HTTP/1.1
```

#### Projects order

Returns the `shoji:order` in which the projects should be displayed for
 the user. This entity is independent for each user.
 
As the user is added to more projects, these will be added at the end of the
`shoji:order`.
 
##### GET

Will return a `shoji:order` containing a flat list of all the projects where
the current user belongs to.


```http
GET /projects/order/ HTTP/1.1
```

```json
{
  "element": "shoji:order",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/order\/",
  "graph": [
    "https://beta.crunch.io/api/projects/cc9161/",
    "https://beta.crunch.io/api/projects/a598c7/"
  ]
}
```

##### PUT

In order to change the order of the projects, the client will need to PUT the
full payload back to the server.

The graph attribute should contain all projects included, else it will return
a 400 response.

After a successful PUT request, the server will reply with a 204 response.

```http
PUT /projects/order/ HTTP/1.1
```

```json
{
  "element": "shoji:order",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/order\/",
  "graph": [
    "https://beta.crunch.io/api/projects/cc9161/",
    "https://beta.crunch.io/api/projects/a598c7/"
  ]
}
```



#### Members

Use this endpoint to manage the users that have access to this project.

##### GET

Returns a catalog with all users that have access to this project in the 
following format:

```http
GET /projects/abcd/members/ HTTP/1.1
```

```json
{
  "element": "shoji:catalog",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/members\/",
  "index": {
    "http:\/\/local.crunch.io:8080\/api\/users\/00002\/": {
      "name": "Jean-Luc Picard",
      "email": "captain@crunch.io"
    },
    "http:\/\/local.crunch.io:8080\/api\/users\/00005\/": {
      "name": "William Riker",
      "email": "firstofficer@crunch.io"
    }
  }
}
```


##### PATCH

Use this method to add or remove members from the project. Only the project owner
has this capabilities, else you will get a 403 response.

To add a new user, PATCH a catalog keyed by the new user URL and an empty
object for its value.

To remove users, PATCH a catalog keyed by the user you want to remove and `null`
for its value.

Note that you cannot remove the project owner from the project, you will
get a 409 response.

It is possible to perform many additions/removals in one request, the 
following example adds users `/users/001/` and deletes users `/users/002/`


```http
PATCH /projects/abcd/members/ HTTP/1.1
```

```json
{
  "element": "shoji:catalog",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/members\/",
  "index": {
    "http:\/\/local.crunch.io:8080\/api\/users\/001\/": {},
    "http:\/\/local.crunch.io:8080\/api\/users\/002\/": null
  }
}
```


#### Datasets

Will list all the datasets that have this project as their owner.

##### GET

Will show the list of all datasets where this project is their owner, the 
shape of the dataset tuple will be the same as in other dataset catalogs.


```http
GET /projects/abcd/datasets/ HTTP/1.1
```

```json
{
  "element": "shoji:catalog",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/datasets\/",
  "orders": {
    "order": "http://local.crunch.io:8080/api/projects/6c01/datasets/order/"
  },
  "index": {
    "https://beta.crunch.io/api/datasets/cc9161/": {
        "owner_name": "James T. Kirk",
        "name": "The Voyage Home",
        "description": "Stardate 8390",
        "archived": false,
        "permissions": {
            "edit": false,
            "change_permissions":,
            "add_users":,
            "change_weight":,
            "view": true
        },
        "size": {
            "rows": 1234,
            "columns": 67
        },
        "id": "cc9161",
        "owner_id": "https://beta.crunch.io/api/users/685722/",
        "start_date": "2286",
        "end_date": null,
        "creation_time": "1986-11-26T12:05:00",
        "current_editor": "https://beta.crunch.io/api/users/ff9443/",
        "current_editor_name": "Leonard Nimoy"
    },
    "https://beta.crunch.io/api/datasets/a598c7/": {
        "owner_name": "Spock",
        "name": "The Wrath of Khan",
        "description": "",
        "archived": false,
        "permissions": {
            "edit": true,
            "change_permissions":,
            "add_users":,
            "change_weight":,
            "view": true
        },
        "size": {
            "rows": null,
            "columns": null
        },
        "id": "a598c7",
        "owner_id": "https://beta.crunch.io/api/users/af432c/",
        "start_date": "2285-10-03",
        "end_date": "2285-10-20",
        "creation_time": "1982-06-04T09:16:23.231045",
        "current_editor": null,
        "current_editor_name": null
    }
  }
}
```

##### PATCH

Same as with members, this endpoint allows to add and remove datasets from the
project.

You can only add datasets that belong to you.

When removing a dataset from a project, their ownership will change from the 
project to you.

To add datasets, include the dataset URL with an empty object in the PATCHed
catalog.

To remove datasets, include the dataset URL with `null` in the PATCHed catalog.

Modifications to the datasets will be reflected in the project's related 
dataset order. 

You can perform multiple additions/removals in one request:


```http
PATCH /projects/abcd/members/ HTTP/1.1
```

```json
{
  "element": "shoji:catalog",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/members\/",
  "index": {
    "https://beta.crunch.io/api/datasets/cc9161/": {},
    "https://beta.crunch.io/api/datasets/a598c7/": null
  }
}
```

#### Icon

The icon endpoint for a project is a ShojiView that allows to change the
project's icon.

##### GET

On GET, it will return a `shoji:view` with its value containing a url to the
icon file or empty string in case there isn't an icon for this project yet.

By default all new projects have an empty icon URL.


```http
GET /projects/abcd/icon/ HTTP/1.1
```


```json
{
  "element": "shoji:view",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/icon\/",
  "value": ""
}
```

##### PUT

PUT to this endpoint to change a project's icon. The payload should have the
 form of a standard multipart/form-data upload. The file's contents will be 
 stored and made available under the project's url.
 
Only the project's owner can change the project's icon.
 
Valid image extensions: 'png', 'gif', 'jpg', 'jpeg' - Others will 400

#### POST

Same as PUT


#### Datasets order

Contains the `shoji:order` in which the datasets of this project are to be 
ordered.

This is endpoint available for all project members but can only be updated by 
the project's owner.


##### GET

Will return the `shoji:order` response containing the datasets that belong
to the project.

```http
GET /projects/6c01/datasets/order/ HTTP/1.1
```

```json
{
  "element": "shoji:order",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/datasets\/order\/",
  "graph": [
    "https://beta.crunch.io/api/datasets/cc9161/",
    "https://beta.crunch.io/api/datasets/a598c7/"
  ]
}
```

##### PUT

Allow to make modifications to the `shoji:order` for the contained datasets.
Only the project owner can make these changes.

Trying to include an invalid dataset or an incomplete list will return a 
400 response.

```http
PUT /projects/6c01/datasets/order/ HTTP/1.1
```

```json
{
  "element": "shoji:order",
  "self": "http:\/\/local.crunch.io:8080\/api\/projects\/6c01\/datasets\/order\/",
  "graph": [
    "https://beta.crunch.io/api/datasets/cc9161/",
    {
      "group": "https://beta.crunch.io/api/datasets/a598c7/"
    }
  ]
}
```
