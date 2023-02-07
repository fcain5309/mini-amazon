select AVG(rs.review)
from Review_Seller rs
group by rs.sellerid