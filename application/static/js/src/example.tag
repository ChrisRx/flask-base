<datatable>
  <form class="col s12" onsubmit="return false">
    <div class="row">
      <div class="input-field col s12">
        <i class="mdi-action-search prefix"></i>
        <input id="search" type="text" class="validate" onkeyup={ edit } autocomplete="off" />
        <label for="search">Search</label>
      </div>
    </div>
  </form>

  <table>
  <thead>
    <tr>
      <th>First Name</th>
      <th>Last Name</th>
      <th>Email</th>
    </tr>
  </thead>
  <tbody>
    <tr each={ items }>
      <td>{ first_name }</td>
      <td>{ last_name }</td>
      <td>{ email }</td>
    </tr>
  </tbody>
  </table>


  <script>
    self = this
    self.items = opts.items

    self.timer = 0

    edit(e) {
      self.text = e.target.value
      if (self.timer) {
        clearTimeout(self.timer)
      }
      if (e.keyCode == 13) {
        self.search(self.text)
      } else {
        self.timer = setTimeout(function() {
          self.search(self.text)
        }, 500)
      }
      return false;
    }

    fetch(url, data, callback, args) {
      $.getJSON(url, data).done(function(json) {
          callback(json.results, args);
        }).fail(function(xhr, status, error) {
          console.log(error);
          return null
        })
    }

    search(q) {
      if (!q) q = " "
      self.fetch("/search", {
        q: q
      }, function(items) {
        self.items = items
        self.update()
      })
      return false;
    }

  </script>

</datatable>
