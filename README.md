# PromoCode
Django Task

[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/built-with-love.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/built-with-swag.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/uses-css.svg)](https://forthebadge.com)

[![forthebadge](https://forthebadge.com/images/badges/uses-git.svg)](https://forthebadge.com)

Please install:
1. `djangorestframework`
2. `django-filter`

Two Models:

1. `PromoCode` - the promo code itself

   | Field     | Type          | Meaning                                                |
   | --------- | ------------- | ------------------------------------------------------ |
   | `code`    | `string`      | the code for the promocode, case insensitive           |
   | `code_l`  | `string`      | automatically set lowercase version of the promocode code |
   | `type`    | `string`      | either `percent` or `value`, how the `value` field should be interpreted |
   | `expires` | `datetime`    | optional field to set when the promocode expires       |
   | `value`   | `decimal`     | the value for the promocode, such as `100` or `0.50`   |
   | `bound`   | `boolean`     | if `true` then the promocode can only be used by the specified user in the `user` field |
   | `user`    | `foreign key` | set when bound to a user                               |
   | `repeat`  | `integer`     | if `0` the promocode can be used infinitely, otherwise it specifies how often any system user can use it |

2. `ClaimedPromoCode` - to track when a user redeems a promocode.

   | Field      | Type          | Meaning                                                |
   | ---------- | ------------- | ------------------------------------------------------ |
   | `redeemed` | `datetime`    | automatically set when a promocode is redeemed            | 
   | `promocode`   | `foreign key` | automatically set to point at the promocode when redeemed |
   | `user`     | `foreign key` | automatically set to point at the promocode when redeemed |
   | `typeOfPayment`| `string` | what type of payment method did the user use when reddeming the code |
   | `company`     | `string` | name of the business company that handeled the transaction |
   | `item`     | `string` | what did the user buy? a ticket? clothes? |
   | `service`     | `string` | what type of service is this? |
   | `total_price`     | `integer` | how much does the transaction cost? |

   

 | API Endpoint                    | Details                                                                                 |
   | --------------------------- | --------------------------------------------------------------------------------------- |
   | `GET /promocode`               | List all promocode in the system, **only superuser can see all**.             |
   | `GET /promocode/{pk}`          | Retrieve details about a promocode by database id                                          |
   | `POST /promocode`              | Create a new promocode                                                                     |
   | `PUT /promocode/{pk}`          | Update a promocode                                                                         |
   | `DELETE /promocode/{pk}`       | Delete a promocode                                                                         |
   | `PUT /promocode/{pk}/redeem`   | Redeem a promocode by database id                                                          |
   | `GET /promocode/{pk}/redeemed` | List all times specified promocode was redeemed, **superuser can see all** |
   | `PATCH /promocode/{pk}`        | **Not supported**                                                                       |
   | `GET /promocode`             | List all redeemed instances, filter-able **only superuser can see all**  | 



