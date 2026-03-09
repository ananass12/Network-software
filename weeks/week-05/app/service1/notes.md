# Для проверки GraphQL

query {
  getTicket(id: "1") { 
    id 
    status 
  }
}
 

query {
  getAllTickets { 
    id 
    status 
  }
}


mutation {
  createTicket(input: {status: "valid"}) { 
    id 
    status 
  }
}


mutation {
  deleteTicket(id: "1")
}